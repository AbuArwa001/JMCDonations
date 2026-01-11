from rest_framework.views import APIView
from rest_framework.response import Response
from transactions.models import Transactions
from rest_framework import permissions

class MpesaCallbackView(APIView):
    authentication_classes = [] 
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        stk_callback = data["Body"]["stkCallback"]
        checkout_id = stk_callback["CheckoutRequestID"]
        result_code = stk_callback["ResultCode"]

        try:
            # Match by the CheckoutRequestID we saved during initiation
            transaction = Transactions.objects.get(transaction_reference=checkout_id)
        except Transactions.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)

        if result_code == 0:
            # Success: Extract metadata
            metadata = stk_callback["CallbackMetadata"]["Item"]
            for entry in metadata:
                if entry["Name"] == "MpesaReceiptNumber":
                    transaction.mpesa_receipt = entry["Value"]
            
            transaction.payment_status = "Completed"
            transaction.completed_at = timezone.now()
        else:
            # Cancelled or Error
            transaction.payment_status = "Failed"
        
        transaction.save()
        return Response({"message": "Callback processed"}, status=200)