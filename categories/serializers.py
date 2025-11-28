from rest_framework import serializers
from .models import Categories

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Categories
        fields = ('id', 'category_name')
        

