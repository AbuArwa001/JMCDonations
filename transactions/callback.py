from rest_framework.views import APIView
from rest_framework.response import Response
from transactions.models import Transactions

class MpesaCallbackView(APIView):
    authentication_classes = []  # Must be open, Safaricom doesn't authenticate

    def post(self, request):
        data = request.data

        checkout_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
        result_code = data["Body"]["stkCallback"]["ResultCode"]
        result_desc = data["Body"]["stkCallback"]["ResultDesc"]

        try:
            transaction = Transactions.objects.get(
                transaction_reference=checkout_id
            )
        except Transactions.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)

        if result_code == 0:
            # Payment successful
            amount = None
            mpesa_receipt = None

            metadata = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

            for entry in metadata:
                if entry["Name"] == "Amount":
                    amount = entry["Value"]
                if entry["Name"] == "MpesaReceiptNumber":
                    mpesa_receipt = entry["Value"]

            transaction.payment_status = "Completed"
            transaction.mpesa_receipt = mpesa_receipt
            transaction.amount = amount
        else:
            transaction.payment_status = "Failed"

        transaction.save()

        return Response({"message": "Callback processed"}, status=200)
