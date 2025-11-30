from rest_framework import serializers
from .models import Transactions


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

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
