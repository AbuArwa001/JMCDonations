from django_filters import FilterSet
from .models import BankAccount, Transactions

class TransactionFilterSet(FilterSet):
    class Meta:
        model = Transactions
        fields = {
            'payment_status': ['exact','icontains'],
            'payment_method': ['exact'],
            'donated_at': ['gte', 'lte'],
            'amount': ['gte', 'lte'],
            'donation': ['exact'],
            'user': ['exact'],
            'account_name': ['icontains'],
            'account_number': ['icontains'],
        }

class BankAccountFilterSet(FilterSet):
    class Meta:
        model = BankAccount
        fields = {
            'is_active': ['exact'],
            'account_name': ['icontains'],
            'account_number': ['icontains'],
        }