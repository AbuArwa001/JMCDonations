from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import AppFeature
from .serializers import AppFeatureSerializer

class AppFeatureViewSet(viewsets.ModelViewSet):
    queryset = AppFeature.objects.all()
    serializer_class = AppFeatureSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
