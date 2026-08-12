from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import JumaKhutba, DeviceToken, NotificationLog
from .serializers import JumaKhutbaSerializer, DeviceTokenSerializer, NotificationLogSerializer
from firebase_admin import messaging

class JumaKhutbaViewSet(viewsets.ModelViewSet):
    queryset = JumaKhutba.objects.all()
    serializer_class = JumaKhutbaSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.action in ['list', 'retrieve'] and not self.request.user.is_staff:
            return JumaKhutba.objects.filter(published=True)
        return super().get_queryset()
        
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DeviceTokenRegisterView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = DeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            fcm_token = serializer.validated_data['fcm_token']
            platform = serializer.validated_data.get('platform', '')
            token, created = DeviceToken.objects.update_or_create(
                fcm_token=fcm_token,
                defaults={'platform': platform}
            )
            return Response({"status": "success", "created": created}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KhutbaNotifyView(views.APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request, pk, *args, **kwargs):
        khutba = get_object_or_404(JumaKhutba, pk=pk)
        
        # Send FCM notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        device_tokens = list(DeviceToken.objects.values_list('fcm_token', flat=True))
        user_tokens = list(User.objects.exclude(fcm_token__isnull=True).exclude(fcm_token='').values_list('fcm_token', flat=True))
        tokens = list(set(device_tokens + user_tokens))
        
        if not tokens:
            return Response({"status": "No devices registered"}, status=status.HTTP_200_OK)
            
        title = f"Friday Khutba: {khutba.title}"
        body = f"Join us this Friday. Imam: {khutba.imam_name} at {khutba.khutba_time.strftime('%I:%M %p')}"
        image_url = request.build_absolute_uri(khutba.imam_photo.url) if khutba.imam_photo else None
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image_url,
            ),
            data={
                'type': 'khutba',
                'khutba_id': str(khutba.id),
            },
            tokens=tokens,
        )
        
        try:
            response = messaging.send_each_for_multicast(message)
            
            # Log it
            NotificationLog.objects.create(
                title=title,
                body=body,
                image_url=image_url,
                related_khutba=khutba,
                recipient_count=response.success_count
            )
            
            return Response({
                "status": "success",
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationLog.objects.all().order_by('-sent_at')
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAdminUser]
