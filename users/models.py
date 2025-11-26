
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class Roles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role_name

class Users(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Keep single token for simplicity, or create separate model for multiple devices
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True, blank=True, default=Roles.objects.get_or_create(role_name='User')[0].id)
    is_admin = models.BooleanField(default=False)
    ss_login = models.DateTimeField(null=True, blank=True)
    
    # Add analytics fields
    firebase_uid = models.CharField(max_length=128, blank=True, null=True)  # If you want to store Firebase UID
    last_analytics_sync = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    def __str__(self):
        return self.email

    @property
    def public_uuid(self):
        """Public UUID for Firebase Analytics user identification"""
        return str(self.id)