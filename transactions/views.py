from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Transactions
from .serializers import TransactionSerializer
from .daraja import MpesaClient
from JMCDonations.authentication import FirebaseAuthentication


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transactions.objects.order_by("-donated_at")
    serializer_class = TransactionSerializer
    authentication_classes = []

    @action(detail=False, methods=["post"])
    def stk_push(self, request):
        phone_number = request.data.get("phone_number")
        amount = request.data.get("amount")
        account_reference = request.data.get("account_reference")
        transaction_desc = request.data.get("transaction_desc")

        if not all([phone_number, amount, account_reference, transaction_desc]):
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )
        

        cl = MpesaClient()
        response = cl.stk_push(
            phone_number, amount, account_reference, transaction_desc
        )
        if response.get("error"):
            return Response(
                response, status=status.HTTP_400_BAD_REQUEST
            )
        elif response.get("ResponseCode") != "0":
            tansaction = Transactions.objects.create(
                amount=amount,
                payment_method="M-Pesa",
                payment_status="Pending",
            )
            serializer = self.get_serializer(tansaction)
            response.update(serializer.data)
        return Response(response)
