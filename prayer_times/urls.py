from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, PrayerTimeAPIView

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')

urlpatterns = [
    path('', PrayerTimeAPIView.as_view(), name='prayer-times-calc'),
    path('', include(router.urls)),
]
