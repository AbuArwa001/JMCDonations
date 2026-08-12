from rest_framework import serializers
from .models import City, PrayerTimeOverride, PrayerCalculationSettings

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class PrayerTimeOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerTimeOverride
        fields = '__all__'

class PrayerCalculationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerCalculationSettings
        fields = '__all__'
