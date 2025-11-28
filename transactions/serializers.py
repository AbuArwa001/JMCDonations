from rest_framework import serializers
from .models import Transactions

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = (
            'id',
            'user',
            'donation',
            'amount',
            'transaction_date',
            'payment_method',
            'status',
        )
