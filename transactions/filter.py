from django_filters import FilterSet
from .models import Transactions

class TransactionFilterSet(FilterSet):
    class Meta:
        model = Transactions
        fields = {
            'payment_status': ['exact','icontains'],
            'payment_method': ['exact'],
            'donated_at': ['gte', 'lte'],
            'amount': ['gte', 'lte'],
        }