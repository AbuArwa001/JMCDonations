from rest_framework.views import APIView
from rest_framework.response import Response
from transactions.models import Transactions
from rest_framework import permissions
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class MpesaCallbackView(APIView):
    authentication_classes = [] 
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        logger.info(f"Mpesa Callback Received: {data}")
        
        try:
            stk_callback = data["Body"]["stkCallback"]
            checkout_id = stk_callback["CheckoutRequestID"]
            result_code = stk_callback["ResultCode"]
            logger.info(f"Processing Callback - CheckoutID: {checkout_id}, ResultCode: {result_code}")
        except KeyError as e:
            logger.error(f"Invalid Callback Data Format: {e}")
            return Response({"error": "Invalid format"}, status=400)

        try:
            # Match by the CheckoutRequestID we saved during initiation
            transaction = Transactions.objects.get(transaction_reference=checkout_id)
        except Transactions.DoesNotExist:
            logger.warning(f"Transaction not found for CheckoutID: {checkout_id}")
            return Response({"error": "Transaction not found"}, status=404)

        if result_code == 0:
            # Success: Extract metadata
            metadata = stk_callback["CallbackMetadata"]["Item"]
            for entry in metadata:
                if entry["Name"] == "MpesaReceiptNumber":
                    transaction.mpesa_receipt = entry["Value"]
            
            transaction.payment_status = "Completed"
            transaction.completed_at = timezone.now()
            transaction.save()
            
            # --- BRIDGE WORKFLOW: Auto-Passthrough for Third-Party Paybills ---
            try:
                donation = transaction.donation
                from django.conf import settings
                jamia_shortcode = getattr(settings, 'MPESA_SHORTCODE', '150770')
                
                if donation and donation.paybill_number and str(donation.paybill_number) != str(jamia_shortcode):
                    logger.info(f"Initiating Bridge Workflow for Donation {donation.id} to {donation.paybill_number}")
                    from transactions.daraja import MpesaClient
                    from transactions.models import Transfer, BankAccount
                    
                    party_b = donation.paybill_number
                    
                    # Log the Transfer intention
                    destination_account = BankAccount.objects.filter(paybill_number=party_b).first()
                    
                    # If this account has Daraja credentials (either on the Donation or the BankAccount), it means STK push went DIRECTLY to them.
                    # Therefore, no B2B bridge is needed.
                    if (donation.consumer_key and donation.consumer_secret) or (destination_account and destination_account.consumer_key and destination_account.consumer_secret):
                        logger.info(f"Donation {donation.id} was paid directly to Third-Party Paybill {party_b}. Skipping B2B Bridge.")
                    else:
                        account_ref = getattr(donation, 'account_number', None)
                        if not account_ref:
                            account_ref = donation.account_name or f"DON-{donation.id}"
                        
                        remarks = f"Passthrough for {donation.title[:20]}"
                        
                        transfer = Transfer.objects.create(
                            amount=transaction.amount,
                            source_paybill=jamia_shortcode,
                            destination_account=destination_account,
                            status="Pending",
                            description=f"Auto B2B Passthrough for Donation {donation.id} - Tx: {transaction.id}"
                        )
                        
                        mpesa = MpesaClient()
                        response = mpesa.b2b_payment(
                            amount=transaction.amount,
                            party_b=party_b,
                            account_reference=account_ref,
                            remarks=remarks
                        )
                        
                        if response and response.get("ResponseCode") == "0":
                            transfer.transaction_reference = response.get("ConversationID")
                            transfer.save()
                            logger.info(f"Bridge Workflow initiated successfully: {response}")
                        else:
                            transfer.status = "Failed"
                            error_msg = response.get('errorMessage') or response.get('ResponseDescription') or 'Unknown Error'
                            transfer.description += f" | M-Pesa Error: {error_msg}"
                            transfer.save()
                            logger.error(f"Bridge Workflow failed: {response}")
            except Exception as e:
                logger.error(f"Error executing Bridge Workflow: {e}", exc_info=True)
                
        else:
            # Cancelled or Error
            transaction.payment_status = "Failed"
            transaction.save()
        
        return Response({"message": "Callback processed"}, status=200)