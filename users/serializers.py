from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)
from .models import Users, UserPaymentAccount


class UserPaymentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPaymentAccount
        fields = (
            "id",
            "account_type",
            "provider",
            "account_number",
            "extra_data",
            "is_default",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class UserCreateSerializer(BaseUserCreateSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta(BaseUserCreateSerializer.Meta):
        model = Users
        fields = {
            "id",
            "email",
            "username",
            "password",
            "full_name",
            "phone_number",
            "is_admin",
            "role",
            "fcm_token",
            "profile_image",
            "profile_image_url",
            "address",
            "bio",
        }

    def create(self, validated_data):
        user = super().create(validated_data)
        return user


class UserSerializer(BaseUserSerializer):
    public_uuid = serializers.ReadOnlyField() 
    full_name=serializers.CharField(required=False)
    username=serializers.CharField(required=False)
    payment_accounts = UserPaymentAccountSerializer(many=True, read_only=True)

    class Meta(BaseUserSerializer.Meta):
        model = Users
        fields = (
            "id",
            "public_uuid",
            "email",
            "username",
            "full_name",
            "phone_number",
            "is_admin",
            "role",
            "fcm_token",
            "profile_image",
            "profile_image_url",
            "address",
            "bio",
            "default_donation_account",
            "payment_accounts",
        )


class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ("fcm_token",)

    def update(self, instance, validated_data):
        instance.fcm_token = validated_data.get("fcm_token", instance.fcm_token)
        instance.save()
        return instance


class UserUUIDSerializer(serializers.Serializer):
    """Serializer for returning user UUID to Flutter after login"""

    user_uuid = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    full_name = serializers.CharField(read_only=True)
