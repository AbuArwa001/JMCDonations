from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from transactions.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.conf import settings
from authentication.backends import FirebaseDRFAuthentication
from transactions.filter import BankAccountFilterSet, TransactionFilterSet
from .models import Transactions, BankAccount
from .serializers import TransactionSerializer, BankAccountSerializer
from .daraja import MpesaClient
from .paypal_client import PayPalClient
from django.utils import timezone
from rest_framework import permissions
import uuid


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    authentication_classes = [FirebaseDRFAuthentication]
    permission_classes = [permissions.AllowAny] 
    filterset_class = TransactionFilterSet

    def get_queryset(self):
        user = self.request.user
        
        # If not authenticated, they get nothing in the list
        if not user or not user.is_authenticated:
            return Transactions.objects.none()
            
        # Admins can see all transactions
        if getattr(user, 'is_admin', False):
            return Transactions.objects.all().order_by("-donated_at")
            
        # Regular users only see their own transactions
        return Transactions.objects.filter(user=user).order_by("-donated_at")

    @action(detail=False, methods=['post'])
    def initiate_stk_push(self, request):
        phone_number = request.data.get('phone_number')
        amount = request.data.get('amount')
        donation_id = request.data.get('donation')
        account_name = request.data.get('account_name')

        # 1. Create the Transaction record as "Pending"
        transaction = Transactions.objects.create(
            donation_id=donation_id,
            user=request.user if request.user.is_authenticated else None,
            amount=amount,
            payment_method="M-Pesa",
            payment_status="Pending",
        )

        # 2. Call M-Pesa
        mpesa = MpesaClient()
        # We use transaction.id as the AccountReference so we can identify it later
        response = mpesa.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_name, 
            transaction_desc=f"Donation to {account_name}"
        )

        # 3. Update with Safaricom's CheckoutID for the callback to find
        if "CheckoutRequestID" in response:
            transaction.transaction_reference = response["CheckoutRequestID"]
            transaction.save()
            return Response(response, status=200)
        
        transaction.payment_status = "Failed"
        transaction.save()
        return Response(response, status=400)

    @action(detail=False, methods=['post'], url_path='complete-test')
    def complete_test_transaction(self, request):
        """
        Manual endpoint to complete a transaction for testing when callbacks can't reach localhost.
        Usage: POST /api/v1/transactions/complete-test/ with {"reference": "checkout_id"}
        """
        reference = request.data.get('reference')
        if not reference:
            return Response({'error': 'reference is required'}, status=400)
        
        try:
            transaction = Transactions.objects.get(transaction_reference=reference)
            transaction.payment_status = "Completed"
            transaction.mpesa_receipt = f"TEST{reference[:10]}"
            transaction.completed_at = timezone.now()
            transaction.save()
            
            return Response({
                'message': 'Transaction marked as completed',
                'transaction': TransactionSerializer(transaction).data
            }, status=200)
        except Transactions.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=404)


    @action(detail=False, methods=['get'])
    def check_status(self, request):
        reference = request.query_params.get('reference')
        if not reference:
            return Response({"error": "Reference is required"}, status=400)
        
        try:
            transaction = Transactions.objects.get(transaction_reference=reference)
            return Response({
                "payment_status": transaction.payment_status,
                "mpesa_receipt": transaction.mpesa_receipt,
                "transaction_id": str(transaction.id),
                "amount": transaction.amount,
            }, status=200)
        except Transactions.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)

    @action(detail=False, methods=['post'])
    def initiate_paypal_payment(self, request):
        amount = request.data.get('amount')
        donation_id = request.data.get('donation')
        
        # 1. Create Pending Transaction
        transaction = Transactions.objects.create(
            donation_id=donation_id,
            user=request.user if request.user.is_authenticated else None,
            amount=amount,
            payment_method="Paypal",
            payment_status="Pending",
        )

        # 2. Call PayPal to create order
        client = PayPalClient()
        # Define return/cancel URLs (adjust domain for production/ngrok)
        # Use simple deep links or a backend callback URL that redirects to app
        # For simplicity, we redirect to a backend callback 
        # that handles capture then redirects to App via Scheme
        callback_url = settings.PAYPAL_CALLBACK_URL
        # OR request.build_absolute_uri('/api/v1/transactions/paypal_callback/')
        
        # Using a fixed one for testing if request.build_absolute_uri is tricky with proxies
        base_url = f"{request.scheme}://{request.get_host()}"
        return_url = f"{base_url}/api/v1/transactions/paypal_callback/?tx_id={transaction.id}"
        cancel_url = f"{base_url}/api/v1/transactions/paypal_callback/?cancel=true&tx_id={transaction.id}"

        order = client.create_order(amount, return_url=return_url, cancel_url=cancel_url)
        
        if order and "id" in order:
            transaction.transaction_reference = order["id"]
            transaction.save()
            
            # Find approval link
            approval_link = next(link["href"] for link in order["links"] if link["rel"] == "approve")
            return Response({"approval_url": approval_link, "transaction_id": transaction.id}, status=200)
        
        transaction.payment_status = "Failed"
        transaction.save()
        return Response({"error": "Failed to create PayPal order"}, status=400)

    @action(detail=False, methods=['get'])
    def paypal_callback(self, request):
        tx_id = request.query_params.get('tx_id')
        token = request.query_params.get('token')
        cancel = request.query_params.get('cancel')
        
        try:
            transaction = Transactions.objects.get(id=tx_id)
        except Transactions.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)

        if cancel == 'true':
            transaction.payment_status = "Failed"
            transaction.save()
            # Redirect to App Deep Link (Failure)
            return redirect("jamiagive://payment/cancel")

        # Capture Order
        client = PayPalClient()
        capture = client.capture_order(token)
        
        if capture and capture["status"] == "COMPLETED":
            transaction.payment_status = "Completed"
            from django.utils import timezone
            transaction.completed_at = timezone.now()
            transaction.save()
            # Redirect to App Deep Link (Success)
            return redirect(f"jamiagive://payment/success?tx_id={transaction.id}")
        
        transaction.payment_status = "Failed"
        transaction.save()
        return redirect("jamiagive://payment/failure")
        return redirect("jamiagive://payment/failure")

    @action(detail=False, methods=['post'])
    def initiate_card_payment(self, request):
        """
        Initiates a Card payment (Flutterwave).
        Creates a pending transaction and returns the tx_ref to be used by the frontend.
        """
        amount = request.data.get('amount')
        donation_id = request.data.get('donation_id')
        
        if not all([amount, donation_id]):
             return Response({"error": "Missing amount or donation_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create Pending Transaction
            transaction = Transactions.objects.create(
                donation_id=donation_id,
                user=request.user if request.user.is_authenticated else None,
                amount=amount,
                payment_method="Card",
                payment_status="Pending",
                # transaction_reference will be auto-generated in save() if not provided, 
                # OR we can generate it here to ensure we have it for the response.
                # Models default is uuid, but let's use a specific ref string if needed.
                # The model uses a UUIDField for ID, but transaction_reference is a CharField.
                # Let's generate a unique ref.
                transaction_reference=f"JM-{uuid.uuid4()}",
                completed_at=None
            )
            
            return Response({
                "message": "Card payment initiated",
                "tx_ref": transaction.transaction_reference,
                "public_key": settings.FLUTTERWAVE_PUBLIC_KEY if hasattr(settings, 'FLUTTERWAVE_PUBLIC_KEY') else "",
                "amount": transaction.amount,
                "currency": "KES"
            }, status=201)
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def verify_flutterwave_payment(self, request):
        """
        Endpoint called by the mobile app after a successful Flutterwave payment.
        Validates the payload and records the transaction.
        """
        tx_ref = request.data.get('tx_ref')
        flw_ref = request.data.get('flw_ref')
        status_param = request.data.get('status') # 'successful'

        # We primarily need tx_ref to find the transaction
        if not tx_ref:
            return Response({"error": "Missing tx_ref"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the existing pending transaction
            try:
                transaction = Transactions.objects.get(transaction_reference=tx_ref)
            except Transactions.DoesNotExist:
                 return Response({"error": "Transaction not found"}, status=404)

            if transaction.payment_status == "Completed":
                return Response({"message": "Transaction already processed"}, status=200)

            # Update Transaction
            if status_param == "successful":
                transaction.payment_status = "Completed"
                transaction.mpesa_receipt = flw_ref # Store Gateway Ref
                transaction.completed_at = timezone.now()
            else:
                transaction.payment_status = "Failed"
            
            transaction.save()
            
            return Response({
                "message": "Transaction updated successfully",
                "transaction_id": transaction.id,
                "status": transaction.payment_status
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.filter(is_active=True)
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseDRFAuthentication]
    filterset_class = BankAccountFilterSet

    @action(detail=False, methods=["post"])
    def stk_push(self, request):
        phone_number = request.data.get("phone_number")
        amount = request.data.get("amount")
        account_reference = request.data.get("account_reference")
        transaction_desc = request.data.get("transaction_desc")
        donation_id = request.data.get("donation")

        if not all([phone_number, amount, account_reference, transaction_desc, donation_id]):
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cl = MpesaClient()
        account_name = request.data.get("account_name") or account_reference
        response = cl.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_name,
            transaction_desc=f"Donation to {account_name}"
        )

        # Error from Daraja
        if response.get("error") or response.get("ResponseCode") != "0":
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Create PENDING transaction
        transaction = Transactions.objects.create(
            amount=amount,
            payment_method="M-Pesa",
            payment_status="Pending",
            transaction_reference=response.get("CheckoutRequestID"),
            donation_id=donation_id,
            user=request.user if request.user.is_authenticated else None,
        )

        # include transaction data in the STK response
        response.update(TransactionSerializer(transaction).data)

        return Response(response, status=200)


from .models import Transfer
from .serializers import TransferSerializer

class TransferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for internal transfers (B2B).
    """
    queryset = Transfer.objects.all().order_by("-created_at")
    serializer_class = TransferSerializer
    authentication_classes = [FirebaseDRFAuthentication]
    permission_classes = [IsAuthenticated] # Maybe IsAdminUser? The user mentioned ADMIN dashboard.

    def create(self, request, *args, **kwargs):
        amount = request.data.get("amount")
        destination_account_id = request.data.get("destination_account")
        description = request.data.get("description", "Transfer from JMC Admin")

        if not amount or not destination_account_id:
            return Response(
                {"error": "Amount and Destination Account are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            destination_account = BankAccount.objects.get(id=destination_account_id)
        except (ValueError, BankAccount.DoesNotExist) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create Pending Transfer Record
        transfer = Transfer.objects.create(
            amount=amount,
            destination_account=destination_account,
            initiated_by=request.user,
            status="Pending",
            description=description,
            source_paybill="150770"
        )

        # 2. Call M-Pesa B2B API
        # Only if destination has a paybill number. If it's a bank account, we need Bank Settlement API (not implemented here per user request "USE B2B API FROM MPESA").
        # B2B API works for Paybill-to-Paybill or Paybill-to-Till directly.
        
        mpesa = MpesaClient()
        party_b = destination_account.paybill_number
        account_ref = destination_account.account_number # For B2B, AccountReference is usually used for reconciliation.
        
        if not party_b:
             # Fallback or Error if user assumes Bank Transfer works via B2B without Paybill
             # Assuming 'Paybill' means Business Paybill
             return Response({"error": "Destination account must have a Paybill Number for B2B transfer"}, status=400)

        response = mpesa.b2b_payment(
            amount=amount,
            party_b=party_b,
            account_reference=account_ref,
            remarks=description
        )

        # 3. Handle Response
        # Success response from M-Pesa B2B is usually synchronous for the request acknowledgment.
        # "ResponseCode": "0" means accepted for processing.
        
        if response.get("ResponseCode") == "0":
            transfer.transaction_reference = response.get("ConversationID") # or OriginatorConversationID
            transfer.save()
            
            return Response({
                "message": "Transfer initiated successfully",
                "transfer": TransferSerializer(transfer).data,
                "mpesa_response": response
            }, status=201)
        else:
            transfer.status = "Failed"
            transfer.description += f" | M-Pesa Error: {response.get('ResponseDescription', 'Unknown Error')}"
            transfer.save()
            return Response(response, status=400)