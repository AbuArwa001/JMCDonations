from rest_framework import serializers
from .models import EventCategory, Event, EventImage

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    gallery_images = EventImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
