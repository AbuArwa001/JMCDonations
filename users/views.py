from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import Users
from .serializers import FCMTokenSerializer, UserUUIDSerializer, UserSerializer

class FCMTokenUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FCMTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['fcm_token']
            request.user.fcm_token = token
            request.user.save()
            
            # Return user UUID for Firebase Analytics setup
            user_data = UserUUIDSerializer({
                'user_uuid': request.user.id,
                'email': request.user.email,
                'full_name': request.user.full_name
            })
            
            return Response({
                'status': 'FCM token updated',
                'user': user_data.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """Get current FCM token"""
        return Response({
            'fcm_token': request.user.fcm_token,
            'user_uuid': request.user.id
        })

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    """Alternative function-based view for FCM token update"""
    serializer = FCMTokenSerializer(data=request.data)
    if serializer.is_valid():
        request.user.fcm_token = serializer.validated_data['fcm_token']
        request.user.save()
        return Response({
            'status': 'success',
            'user_uuid': str(request.user.id),
            'message': 'FCM token updated successfully'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)