from rest_framework import serializers
from .models import NisabRate

class NisabRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NisabRate
        fields = '__all__'
        read_only_fields = ('updated_at', 'updated_by')
