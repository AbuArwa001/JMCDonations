from django.db import models
from django.conf import settings
import uuid


class Transactions(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    )
    PAYMENT_METHOD_CHOICES = (
        ("Cash", "Cash"),
        ("Card", "Card"),
        ("M-Pesa", "M-Pesa"),
        ("Paypal", "Paypal"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation = models.ForeignKey(
        "donations.Donations", on_delete=models.CASCADE, related_name="transactions"
    )
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    recorded_by_admin_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_transactions",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_reference = models.CharField(
        max_length=100, unique=True, blank=True, null=True
    )
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="Pending"
    )
    mpesa_receipt = models.CharField(max_length=50, blank=True, null=True)
    donated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.account_name:
            self.account_name = self.donation.account_name
        if not self.account_number:
            self.account_number = self.donation.paybill_number
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.amount} - {self.donation.title}"


class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=100)
    paybill_number = models.CharField(max_length=50, blank=True, null=True, help_text="Paybill Business Number")
    account_number = models.CharField(max_length=50, help_text="Account Number/Reference")
    account_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class Transfer(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_paybill = models.CharField(max_length=50, default="150770")
    destination_account = models.ForeignKey(
        BankAccount, on_delete=models.SET_NULL, null=True, related_name="transfers_received"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="initiated_transfers",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transfer of {self.amount} to {self.destination_account}"
