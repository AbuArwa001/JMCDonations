from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import CommunityContent
from .serializers import CommunityContentSerializer

class CommunityContentViewSet(viewsets.ModelViewSet):
    queryset = CommunityContent.objects.all().order_by('-created_at')
    serializer_class = CommunityContentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content_type', 'is_published']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True)
        return queryset
