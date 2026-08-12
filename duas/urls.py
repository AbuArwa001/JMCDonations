from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DuaCategoryViewSet, DuaViewSet

router = DefaultRouter()
router.register(r'categories', DuaCategoryViewSet, basename='dua-category')
router.register(r'', DuaViewSet, basename='dua')

urlpatterns = [
    path('', include(router.urls)),
]
