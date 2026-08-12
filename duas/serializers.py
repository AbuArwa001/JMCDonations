from rest_framework import serializers
from .models import DuaCategory, Dua

class DuaCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DuaCategory
        fields = '__all__'

class DuaSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Dua
        fields = '__all__'
