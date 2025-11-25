from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from .models import Users

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = Users
        fields = ('id', 'email', 'username', 'password', 'full_name', 'phone_number')
    
    def create(self, validated_data):
        user = super().create(validated_data)
        # User gets automatic UUID from model default
        return user

class UserSerializer(BaseUserSerializer):
    public_uuid = serializers.ReadOnlyField()  # Expose the UUID to Flutter
    
    class Meta(BaseUserSerializer.Meta):
        model = Users
        fields = ('id', 'public_uuid', 'email', 'username', 'full_name', 'phone_number', 'is_admin', 'role', 'fcm_token')

class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('fcm_token',)
    
    def update(self, instance, validated_data):
        instance.fcm_token = validated_data.get('fcm_token', instance.fcm_token)
        instance.save()
        return instance

class UserUUIDSerializer(serializers.Serializer):
    """Serializer for returning user UUID to Flutter after login"""
    user_uuid = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    full_name = serializers.CharField(read_only=True)