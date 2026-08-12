from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, PrayerTimeAPIView, PrayerTimeOverrideViewSet, PrayerCalculationSettingsAPIView

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'overrides', PrayerTimeOverrideViewSet, basename='override')

urlpatterns = [
    path('settings/', PrayerCalculationSettingsAPIView.as_view(), name='prayer-settings'),
    path('', PrayerTimeAPIView.as_view(), name='prayer-times-calc'),
    path('', include(router.urls)),
]
