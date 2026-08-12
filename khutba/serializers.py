from rest_framework import serializers
from .models import JumaKhutba, DeviceToken, NotificationLog

class JumaKhutbaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JumaKhutba
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['fcm_token', 'platform']

class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = '__all__'
