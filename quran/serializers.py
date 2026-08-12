from rest_framework import serializers
from .models import Reciter, SurahAudio

class ReciterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciter
        fields = '__all__'

class SurahAudioSerializer(serializers.ModelSerializer):
    reciter_name = serializers.CharField(source='reciter.name', read_only=True)
    
    class Meta:
        model = SurahAudio
        fields = '__all__'
