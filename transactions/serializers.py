from rest_framework import serializers

from donations.serializers import DonationSerializer
from users.serializers import UserSerializer
from .models import Transactions


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)
    donation = DonationSerializer(read_only=True)

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