from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DonationViewSet,
    DonationHistoryView,
    ReceiptView,
)

router = DefaultRouter()
router.register(r"donations", DonationViewSet) # This now handles list, retrieve, save, unsave, and saved

urlpatterns = [
    path("", include(router.urls)),
    path("users/history/", DonationHistoryView.as_view(), name="donation-history"),
    path("transactions/<uuid:pk>/receipt/", ReceiptView.as_view(), name="receipt"),
]