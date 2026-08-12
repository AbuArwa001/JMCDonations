from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import EventCategory, Event, EventImage
from .serializers import EventCategorySerializer, EventSerializer, EventImageSerializer
from firebase_admin import messaging
from khutba.models import DeviceToken, NotificationLog

class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
        
    def get_queryset(self):
        if self.action in ['list', 'retrieve'] and not self.request.user.is_staff:
            return Event.objects.filter(published=True)
        return super().get_queryset()
        
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class EventNotifyView(views.APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request, pk, *args, **kwargs):
        event = get_object_or_404(Event, pk=pk)
        
        tokens = list(DeviceToken.objects.values_list('fcm_token', flat=True))
        if not tokens:
            return Response({"status": "No devices registered"}, status=status.HTTP_200_OK)
            
        title = f"Upcoming Event: {event.title}"
        body = f"Join us on {event.event_date.strftime('%B %d, %Y')} at {event.venue_name}."
        image_url = request.build_absolute_uri(event.cover_image.url) if event.cover_image else None
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image_url,
            ),
            data={
                'type': 'event',
                'event_id': str(event.id),
            },
            tokens=tokens,
        )
        
        try:
            response = messaging.send_each_for_multicast(message)
            
            NotificationLog.objects.create(
                title=title,
                body=body,
                image_url=image_url,
                related_event=event,
                recipient_count=response.success_count
            )
            
            return Response({
                "status": "success",
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EventImageViewSet(viewsets.ModelViewSet):
    queryset = EventImage.objects.all()
    serializer_class = EventImageSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
