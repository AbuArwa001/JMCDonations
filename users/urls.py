from django.urls import path
from .views import (
    FCMTokenUpdateView,
    FirebaseLoginView,
    UserProfileView,
    UserViewSet,
    UserPaymentAccountViewSet,
)
from .admin_auth_views import FirebaseAdminLoginView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"payment-accounts", UserPaymentAccountViewSet, basename="payment-account")

urlpatterns = [
    path('auth/firebase/login/', FirebaseLoginView.as_view(), name='firebase_login'),
    path("", UserViewSet.as_view({"get": "list"}), name="user_list"),
    # path('<uuid:pk>/', UserViewSet.as_view({'get': 'get'}), name='user_detail'),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("register/", UserProfileView.as_view(), name="user_register"),
    path("update-fcm-token/", FCMTokenUpdateView.as_view(), name="update_fcm_token"),
    path("admin-firebase-login/", FirebaseAdminLoginView.as_view(), name="admin_firebase_login"),
] + router.urls
