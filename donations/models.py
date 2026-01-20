# from datetime import timezone
from django.utils import timezone
from django.db import models
from django.conf import settings
import uuid
from django.utils.text import slugify
from django.db.models import JSONField

def donation_image_upload_path(instance, filename):
    # jmcdonations/[donationDriveslug]/[image name].jpg
    # Assuming the bucket is the root, so we return the key path.
    # We strip 'donations/' prefix to match user request of jmcdonations/[slug]/...
    return f'{instance.donation.slug}/{filename}'


class Donations(models.Model):
    STATUS_CHOICES = (
        ("Active", "Active"),
        ("Closed", "Closed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    image_urls = JSONField(default=list, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    paybill_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    category = models.ForeignKey(
        "categories.Categories", on_delete=models.CASCADE, related_name="donations"
    )
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=False)
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
    def donor_count(self):
        return self.transactions.values('user').distinct().count()
    def __str__(self):
        return self.title
    def is_expired(self):
        """Check if donation end date has passed"""
        # print(self.end_date, timezone.now())
        return self.end_date < timezone.now()
    
    def should_be_closed(self):
        """Check if donation should be closed (expired and still active)"""
        return self.is_expired() and self.status == 'Active'
    
    def close_if_expired(self, save=True):
        """Close the donation if it's expired and active"""
        if self.should_be_closed():
            self.status = 'Closed'
            if save:
                self.save(update_fields=['status'])
            return True
        return False
    
    @classmethod
    def close_all_expired(cls):
        """Close all expired donations in bulk"""
        from django.utils import timezone
        now = timezone.now()
        
        expired_count = cls.objects.filter(
            end_date__lt=now,
            status='Active'
        ).update(status='Closed')
        
        return expired_count
    
    # You can also add a save method to auto-close if expired
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Donations.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1

        # Auto-close if end date has passed
        if self.is_expired():
            self.status = 'Closed'
        
        super().save(*args, **kwargs)

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
 
# class DonationImage(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     donation = models.ForeignKey(
#         Donations, on_delete=models.CASCADE, related_name="images"
#     )
#     image = models.ImageField(upload_to=donation_image_upload_path)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Image for {self.donation.title}"
