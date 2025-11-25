
from django.urls import path
from .views import FCMTokenUpdateView

urlpatterns = [
    path('update-fcm-token/', FCMTokenUpdateView.as_view(), name='update_fcm_token'),
]
