from rest_framework import serializers
from .models import City, PrayerTimeOverride

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class PrayerTimeOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerTimeOverride
        fields = '__all__'
