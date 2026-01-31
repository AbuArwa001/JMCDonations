from django.urls import path, include
from rest_framework.routers import DefaultRouter

from transactions.callback import MpesaCallbackView
from .views import TransactionViewSet, BankAccountViewSet, TransferViewSet

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transactions")
router.register(r"bank-accounts", BankAccountViewSet, basename="bank-accounts")
router.register(r"transfers", TransferViewSet, basename="transfers")


urlpatterns = [
    path("mpesa/callback/", MpesaCallbackView.as_view(), name="mpesa-callback"),
]

urlpatterns += router.urls
