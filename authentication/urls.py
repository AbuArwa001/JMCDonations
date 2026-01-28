
from django.urls import path
from .views import AdminFirebaseBridge

urlpatterns = [
    path('auth/bridge/', AdminFirebaseBridge.as_view(), name='admin-bridge'),
]