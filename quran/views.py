from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Reciter, SurahAudio
from .serializers import ReciterSerializer, SurahAudioSerializer

class ReciterViewSet(viewsets.ModelViewSet):
    queryset = Reciter.objects.all()
    serializer_class = ReciterSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class SurahAudioViewSet(viewsets.ModelViewSet):
    queryset = SurahAudio.objects.all()
    serializer_class = SurahAudioSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['surah_number', 'reciter']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
