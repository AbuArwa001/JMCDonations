from rest_framework import serializers

from donations.serializers import DonationSerializer
from users.serializers import UserSerializer
from .models import Transactions, BankAccount


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)
    donation = DonationSerializer(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    account_name = serializers.CharField(read_only=True)
    account_number = serializers.CharField(read_only=True)

    class Meta:
        model = Transactions
        fields = (
            "id",
            "user",
            "donation",
            "amount",
            "donated_at",
            "payment_method",
            "payment_status",
            "transaction_reference",
            "mpesa_receipt",
            "account_name",
            "account_number",
        )
        extra_kwargs = {
            "payment_method": {"read_only": True},
            "donated_at": {"read_only": True},
        }





class BankAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for BankAccount model.
    returns bank account details.
    example:
    {
        "id": "uuid",
        "bank_name": "Bank of Example",
        "account_number": "1234567890",
        "account_name": "John Doe",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    """
    class Meta:
        model = BankAccount
        fields = (
            "id",
            "bank_name",
            "account_number",
            "account_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")