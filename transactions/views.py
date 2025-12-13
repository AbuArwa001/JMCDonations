from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from transactions.filter import TransactionFilterSet
from .models import Transactions
from .serializers import TransactionSerializer
from .daraja import MpesaClient


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transactions.objects.order_by("-payment_status")
    serializer_class = TransactionSerializer
    authentication_classes = []
    filterset_class = TransactionFilterSet

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
    def list(self, request, *args, **kwargs):
        print("Filterset:", self.filterset_class)
        print("Query params:", request.query_params)
        return super().list(request, *args, **kwargs)