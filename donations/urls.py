from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonationViewSet, SavedDonationView, UnsaveDonationView, DonationHistoryView, ReceiptView

router = DefaultRouter()
router.register(r'donations', DonationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('saved-donations/', SavedDonationView.as_view(), name='saved-donations'),
    path('<uuid:pk>/save/', SavedDonationView.as_view(), name='save-donation'),
    path('<uuid:pk>/unsave/', UnsaveDonationView.as_view(), name='unsave-donation'),
    path('users/history/', DonationHistoryView.as_view(), name='donation-history'),
    path('transactions/<uuid:pk>/receipt/', ReceiptView.as_view(), name='receipt'),
]
