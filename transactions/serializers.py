from rest_framework import serializers

from donations.serializers import DonationSerializer
from users.serializers import UserSerializer
from .models import Transactions, BankAccount, Transfer


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
    """
    class Meta:
        model = BankAccount
        fields = (
            "id",
            "bank_name",
            "paybill_number",
            "account_number",
            "account_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TransferSerializer(serializers.ModelSerializer):
    """
    Serializer for Transfer model.
    """
    destination_account_details = BankAccountSerializer(source='destination_account', read_only=True)
    initiated_by_name = serializers.CharField(source='initiated_by.get_full_name', read_only=True)

    class Meta:
        model = Transfer
        fields = (
            "id",
            "source_paybill",
            "destination_account",
            "destination_account_details",
            "amount",
            "initiated_by",
            "initiated_by_name",
            "status",
            "transaction_reference",
            "description",
            "created_at",
            "completed_at",
        )
        read_only_fields = (
            "id", 
            "initiated_by", 
            "status", 
            "transaction_reference", 
            "created_at", 
            "completed_at",
            "source_paybill"
        )