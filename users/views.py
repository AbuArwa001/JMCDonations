from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import Users
from .serializers import FCMTokenSerializer, UserUUIDSerializer, UserSerializer


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
    authentication_classes = [] # This endpoint should not require existing auth
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

            if not email:
                 return Response({'error': 'Firebase account missing email address'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Create or update the local Django user using firebase_uid as the unique identifier
            user, created = Users.objects.get_or_create(
                firebase_uid=firebase_uid,
                defaults={
                    'email': email,
                    # Ensure username is set if your model requires it
                    'username': email.split('@')[0], 
                    'full_name': full_name,
                    'is_active': True,
                    'ss_login': timezone.now(), # Update last sign in time
                }
            )
            
            # If user already existed, ensure fields are updated
            if not created:
                user.email = email
                user.full_name = full_name
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

    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(Users, pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            users = Users.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)


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
