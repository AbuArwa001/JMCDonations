from rest_framework import serializers
from .models import CommunityContent

class CommunityContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityContent
        fields = ['id', 'content_type', 'title', 'body', 'author_or_sheikh', 'scheduled_for', 'is_published', 'created_at']
        read_only_fields = ['created_at']
