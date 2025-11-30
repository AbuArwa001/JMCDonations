from django.db import models
from django.conf import settings
import uuid


class Donations(models.Model):
    STATUS_CHOICES = (
        ("Active", "Active"),
        ("Closed", "Closed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    paybill_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    category = models.ForeignKey(
        "categories.Categories", on_delete=models.CASCADE, related_name="donations"
    )
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_donations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(r.rating for r in ratings) / ratings.count()
        return 0

    def __str__(self):
        return self.title


class SavedDonations(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_donations",
    )
    donation = models.ForeignKey(
        Donations, on_delete=models.CASCADE, related_name="saved_by"
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "donation")