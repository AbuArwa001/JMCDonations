from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReciterViewSet, SurahAudioViewSet

router = DefaultRouter()
router.register(r'reciters', ReciterViewSet, basename='reciter')
router.register(r'audio', SurahAudioViewSet, basename='surah-audio')

urlpatterns = [
    path('', include(router.urls)),
]
