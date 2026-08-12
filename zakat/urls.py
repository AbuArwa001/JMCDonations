from django.urls import path
from .views import NisabRateAPIView

urlpatterns = [
    path('nisab-rate/', NisabRateAPIView.as_view(), name='nisab-rate'),
]
