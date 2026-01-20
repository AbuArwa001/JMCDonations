from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DonationViewSet,
    DonationImageViewSet,
    DonationHistoryView,
    ReceiptView,
)

router = DefaultRouter()
router.register(r"donations", DonationViewSet)
router.register(r"donation-images", DonationImageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("users/history/", DonationHistoryView.as_view(), name="donation-history"),
    path("transactions/<uuid:pk>/receipt/", ReceiptView.as_view(), name="receipt"),
]