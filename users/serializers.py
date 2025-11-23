from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from .models import Users

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = Users
        fields = ('id', 'email', 'username', 'password', 'full_name', 'phone_number')

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = Users
        fields = ('id', 'email', 'username', 'full_name', 'phone_number', 'is_admin', 'role')
