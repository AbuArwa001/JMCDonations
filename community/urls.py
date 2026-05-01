from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityContentViewSet

router = DefaultRouter()
router.register(r'content', CommunityContentViewSet, basename='community-content')

urlpatterns = [
    path('community/', include(router.urls)),
]
