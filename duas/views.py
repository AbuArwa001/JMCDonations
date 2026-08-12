from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import DuaCategory, Dua
from .serializers import DuaCategorySerializer, DuaSerializer

class DuaCategoryViewSet(viewsets.ModelViewSet):
    queryset = DuaCategory.objects.all()
    serializer_class = DuaCategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class DuaViewSet(viewsets.ModelViewSet):
    queryset = Dua.objects.all()
    serializer_class = DuaSerializer
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
            return Dua.objects.filter(published=True)
        return super().get_queryset()
