from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser
import uuid


def profile_image_upload_path(instance, filename):
    # profiles/[username].jpg
    ext = filename.split('.')[-1]
    return f'profiles/{instance.username}.{ext}'


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
    role = models.ForeignKey(
        Roles, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    is_admin = models.BooleanField(default=False)
    ss_login = models.DateTimeField(null=True, blank=True)

    # Add analytics fields
    firebase_uid = models.CharField(
        max_length=128, blank=True, null=True
    )  # to store Firebase UID
    last_analytics_sync = models.DateTimeField(null=True, blank=True)

    # Profile fields
    profile_image = models.ImageField(upload_to=profile_image_upload_path, blank=True, null=True)
    profile_image_url = models.CharField(max_length=500, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    default_donation_account = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "full_name"]

    def __str__(self):
        return self.email

    @property
    def public_uuid(self):
        """Public UUID for Firebase Analytics user identification"""
        return str(self.id)

    @property
    def total_donations(self):
        return self.transactions.filter(payment_status="Completed").count()

    @property
    def total_impact(self):
        result = self.transactions.filter(payment_status="Completed").aggregate(
            total=Sum("amount")
        )
        return result["total"] or 0.0

    def save(self, *args, **kwargs):
        if not self.role:
            self.role, created = Roles.objects.get_or_create(role_name="User")
        
        # Sync profile_image_url if an image is uploaded
        if self.profile_image:
            self.profile_image_url = self.profile_image.url
            
        super().save(*args, **kwargs)


class UserPaymentAccount(models.Model):
    ACCOUNT_TYPES = (
        ('M-Pesa', 'M-Pesa'),
        ('Card', 'Card'),
        ('PayPal', 'PayPal'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="payment_accounts"
    )
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    provider = models.CharField(max_length=50, blank=True, null=True) # Safaricom, Visa, etc.
    account_number = models.CharField(max_length=100) # Phone, Card Last 4, Email
    extra_data = models.JSONField(default=dict, blank=True) # Masked card info, Till number etc.
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            UserPaymentAccount.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account_type} - {self.account_number} ({self.user.email})"
