from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from transactions.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.conf import settings
from authentication.backends import FirebaseAuthentication
from transactions.filter import BankAccountFilterSet, TransactionFilterSet
from .models import Transactions, BankAccount
from .serializers import TransactionSerializer, BankAccountSerializer
from .daraja import MpesaClient
from .paypal_client import PayPalClient
from django.utils import timezone
from rest_framework import permissions


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transactions.objects.order_by("-payment_status")
    serializer_class = TransactionSerializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [permissions.AllowAny]  # Allow both authenticated and anonymous
    filterset_class = TransactionFilterSet

    @action(detail=False, methods=['post'])
    def initiate_stk_push(self, request):
        phone_number = request.data.get('phone_number')
        amount = request.data.get('amount')
        donation_id = request.data.get('donation')

        # 1. Create the Transaction record as "Pending"
        transaction = Transactions.objects.create(
            donation_id=donation_id,
            user=request.user if request.user.is_authenticated else None,
            amount=amount,
            payment_method="M-Pesa",
            payment_status="Pending"
        )

        # 2. Call M-Pesa
        mpesa = MpesaClient()
        # We use transaction.id as the AccountReference so we can identify it later
        response = mpesa.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=str(transaction.id)[:12], 
            transaction_desc=f"Donation {donation_id}"
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
            payment_status="Pending"
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

class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.filter(is_active=True)
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseAuthentication]
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
        response = cl.stk_push(
            phone_number,
            amount,
            account_reference,
            transaction_desc
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

        serializer = self.get_serializer(transaction)

        # include transaction data in the STK response
        response.update(serializer.data)

        return Response(response, status=200)

    @action(detail=False, methods=["post"])
    def transfer(self, request):
        amount = request.data.get("amount")
        
        if not amount:
            return Response(
                {"error": "Amount is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
             return Response(
                {"error": "Invalid amount"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Simulate B2B Transfer
        # In a real scenario, this would call MpesaClient().b2b_payment(...)
        
        # Create transaction record
        transaction = Transactions.objects.create(
            amount=amount,
            payment_method="Transfer", # Custom method for transfers
            payment_status="Completed", # Assume instant success for simulation
            transaction_reference=f"TRX-{timezone.now().timestamp()}",
            user=request.user if request.user.is_authenticated else None,
            # donation=None # Transfers might not be linked to a specific donation drive
        )
        
        return Response({
            "message": "Transfer initiated successfully",
            "transaction_id": transaction.id,
            "amount": amount,
            "status": "Completed"
        })

    def list(self, request, *args, **kwargs):
        print("Filterset:", self.filterset_class)
        print("Query params:", request.query_params)
        return super().list(request, *args, **kwargs)