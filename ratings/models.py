from django.db import models
from django.conf import settings
import uuid


class Ratings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings"
    )
    donation = models.ForeignKey(
        "donations.Donations", on_delete=models.CASCADE, related_name="ratings"
    )
    comment = models.TextField()
    rating = models.FloatField()

    class Meta:
        unique_together = ("user", "donation")
