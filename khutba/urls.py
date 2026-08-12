from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JumaKhutbaViewSet, KhutbaNotifyView, DeviceTokenRegisterView

router = DefaultRouter()
router.register(r'', JumaKhutbaViewSet, basename='khutba')

urlpatterns = [
    path('register-device/', DeviceTokenRegisterView.as_view(), name='register-device'),
    path('<int:pk>/notify/', KhutbaNotifyView.as_view(), name='khutba-notify'),
    path('', include(router.urls)),
]
