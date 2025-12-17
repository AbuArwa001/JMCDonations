from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from transactions.permissions import IsAuthenticated

from authentication.backends import FirebaseAuthentication
from transactions.filter import BankAccountFilterSet, TransactionFilterSet
from .models import Transactions, BankAccount
from .serializers import TransactionSerializer, BankAccountSerializer
from .daraja import MpesaClient
from django.utils import timezone
from rest_framework import permissions


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transactions.objects.order_by("-payment_status")
    serializer_class = TransactionSerializer
    authentication_classes = []
    filterset_class = TransactionFilterSet


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

        if not all([phone_number, amount, account_reference, transaction_desc]):
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