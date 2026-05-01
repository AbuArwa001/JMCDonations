from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppFeatureViewSet

router = DefaultRouter()
router.register(r'features', AppFeatureViewSet, basename='features')

urlpatterns = [
    path('', include(router.urls)),
]
