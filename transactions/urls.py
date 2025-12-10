from django.urls import path, include
from rest_framework.routers import DefaultRouter

from transactions.callback import MpesaCallbackView
from .views import TransactionViewSet

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transactions")


urlpatterns = [
    path("mpesa/callback/", MpesaCallbackView.as_view(), name="mpesa-callback"),
]

urlpatterns += router.urls
