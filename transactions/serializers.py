from rest_framework import serializers

from donations.serializers import DonationSerializer
from users.serializers import UserSerializer
from .models import Transactions


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)
    donation = DonationSerializer(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

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
        )
        extra_kwargs = {
            "payment_method": {"read_only": True},
            "donated_at": {"read_only": True},
        }