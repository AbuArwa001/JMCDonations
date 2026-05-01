from rest_framework import serializers
from .models import AppFeature

class AppFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeature
        fields = ['id', 'name', 'is_active', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
