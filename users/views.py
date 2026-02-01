import os
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import os
import firebase_admin
# from django.conf import settings
from JMCDonations import settings
from authentication.backends import FirebaseDRFAuthentication
from users.permissions import IsAdminOrSelf, IsAdminUser
from .models import Users, UserPaymentAccount
from .serializers import (
    FCMTokenSerializer,
    UserUUIDSerializer,
    UserSerializer,
    UserPaymentAccountSerializer,
)


class UserPaymentAccountViewSet(viewsets.ModelViewSet):
    serializer_class = UserPaymentAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPaymentAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# In /home/khalfan/Documents/JMCDonations/JMCDonations/views.py (or wherever your views file is)

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.utils import timezone

# Import Firebase Admin Auth and SimpleJWT
from firebase_admin import auth 
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Users
from .serializers import FCMTokenSerializer, UserUUIDSerializer, UserSerializer

# Get the custom User model reference
Users = get_user_model()


class FirebaseLoginView(APIView):
    """
    Accepts a Firebase ID Token, verifies it, and returns
    Django/Djoser compatible Access and Refresh JWTs.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        id_token = request.data.get('idToken') # Client sends token in 'idToken' field

        if not id_token:
            return Response({'error': 'Firebase ID token required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Verify the token using Firebase Admin SDK
            decoded_token = auth.verify_id_token(id_token)
            
            # Extract key data from Firebase payload
            firebase_uid = decoded_token['uid']
            email = decoded_token.get('email')
            full_name = decoded_token.get('name', '')
            picture = decoded_token.get('picture')

            if not email:
                 return Response({'error': 'Firebase account missing email address'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Optimized user lookup: check by firebase_uid first, then email
            try:
                user = Users.objects.get(firebase_uid=firebase_uid)
                created = False
            except Users.DoesNotExist:
                try:
                    # Look for existing user by email
                    user = Users.objects.get(email=email)
                    user.firebase_uid = firebase_uid
                    user.save()
                    created = False
                    print(f"✅ Linked existing user {email} to firebase_uid")
                except Users.DoesNotExist:
                    # New user entirely
                    base_username = email.split('@')[0]
                    username = base_username
                    import random
                    
                    # Ensure username uniqueness
                    while Users.objects.filter(username=username).exists():
                         username = f"{base_username}{random.randint(1000, 9999)}"

                    user = Users.objects.create(
                        firebase_uid=firebase_uid,
                        email=email,
                        username=username, 
                        full_name=full_name,
                        profile_image_url=picture,
                        is_active=True,
                    )
                    created = True
                    print(f"✅ Created new user {email} with username {username}")

            # Ensure fields are updated upon login
            user.full_name = full_name or user.full_name
            if picture and not user.profile_image:
                 user.profile_image_url = picture
            user.ss_login = timezone.now()
            user.save()

            # 3. Generate Djoser/SimpleJWT tokens for the user
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user, context={'request': request}).data, 
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        except auth.InvalidIdTokenError:
            return Response({'error': 'Invalid Firebase ID token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e), 'detail': 'Firebase authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)

class FCMTokenUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FCMTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["fcm_token"]
            request.user.fcm_token = token
            request.user.save()

            # Return user UUID for Firebase Analytics setup
            user_data = UserUUIDSerializer(
                {
                    "user_uuid": request.user.id,
                    "email": request.user.email,
                    "full_name": request.user.full_name,
                }
            )

            return Response(
                {"status": "FCM token updated", "user": user_data.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """Get current FCM token"""
        return Response(
            {"fcm_token": request.user.fcm_token, "user_uuid": request.user.id}
        )


class UserProfileView(APIView):
    """Get user profile including UUID for Firebase setup"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user-related operations"""

    queryset = Users.objects.order_by('-date_joined')
    serializer_class = UserSerializer
    authentication_classes = [FirebaseDRFAuthentication]
    permission_classes = [IsAdminOrSelf]

    def get_object(self):
        """
        Override get_object to allow lookup by either PK (UUID) or firebase_uid.
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs.get(lookup_url_kwarg)

        try:
            # Try standard lookup (UUID)
            obj = get_object_or_404(queryset, pk=lookup_value)
        except:
            # If that fails (e.g. not a UUID), try firebase_uid
            obj = get_object_or_404(queryset, firebase_uid=lookup_value)

        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request, *args, **kwargs):
        """
        Only admins can list all users.
        """
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=403
            )
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Normal users may retrieve only themselves.
        Admins may retrieve anyone.
        """
        return super().retrieve(request, *args, **kwargs)
    def perform_update(self, serializer):
        """Ensure only admins can update other users"""
        if self.get_object() != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to update this user.")
        return super().perform_update(serializer)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    """Alternative function-based view for FCM token update"""
    serializer = FCMTokenSerializer(data=request.data)
    if serializer.is_valid():
        request.user.fcm_token = serializer.validated_data["fcm_token"]
        request.user.save()
        return Response(
            {
                "status": "success",
                "user_uuid": str(request.user.id),
                "message": "FCM token updated successfully",
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FirebaseCheckView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Debug endpoint to check Firebase status"""
        try:
            # Try to get Firebase app
            app = firebase_admin.get_app()
            return Response({
                "status": "success",
                "message": "Firebase initialized",
                "app_name": app.name,
                "env_var_set": bool(os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')),
                "path_exists": os.path.exists(os.path.join(settings.BASE_DIR, 'config', 'jmcdonations.json'))
            })
        except ValueError:
            return Response({
                "status": "error", 
                "message": "Firebase not initialized",
                "env_var_set": bool(os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')),
                "env_var_length": len(os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON', ''))
            }, status=500)