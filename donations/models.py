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
        ("Completed", "Completed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    image_urls = models.JSONField(default=list, blank=True)
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
    notification_sent = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(r.rating for r in ratings) / ratings.count()
        return 0
    def donor_count(self):
        return self.transactions.values('user').distinct().count()
    def __str__(self):
        return self.title
    @property
    def remaining_days(self):
        """Calculate days remaining until end_date"""
        if not self.end_date:
            return 0
        delta = self.end_date - timezone.now()
        # Using .days returns the number of full days. 
        # If it's 10:30 AM and end_date is 10:00 AM same day, it's -1 or 0? 
        # Actually delta.days is usually what we want.
        return delta.days

    def is_expired(self):
        return self.remaining_days < 0

    @property
    def collected_amount(self):
        """Calculate total from completed transactions only"""
        total = self.transactions.filter(
            payment_status="Completed"
        ).aggregate(total=models.Sum('amount'))['total']
        return total if total else 0

    def auto_update_status(self, save=True):
        """
        Main logic to close or complete a donation based on:
        1. Funding (collected >= target) -> Completed
        2. Time (days remaining < 0) -> Closed
        """
        if self.status != 'Active':
            return False

        updated = False
        
        # Check funding first (priority)
        if self.collected_amount >= self.target_amount:
            self.status = 'Completed'
            updated = True
        # Then check expiration
        elif self.is_expired():
            self.status = 'Closed'
            updated = True

        if updated and save:
            self.save(update_fields=['status'])
        
        return updated

    def check_and_close_if_funded(self, save=True):
        """Legacy method for backward compatibility/signals"""
        return self.auto_update_status(save=save)

    def should_be_closed(self):
        """Check if donation should be closed (expired or funded) and still active"""
        return self.status == 'Active' and (self.is_expired() or self.collected_amount >= self.target_amount)
    
    def close_if_expired(self, save=True):
        """Close the donation if it's expired or funded and active"""
        return self.auto_update_status(save=save)
    
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

        # Auto-update status based on time and funding
        if self.status == 'Active':
            # We don't call auto_update_status here to avoid potential recursion 
            # if it calls save(), but we apply the same logic.
            if self.collected_amount >= self.target_amount:
                self.status = 'Completed'
            elif self.is_expired():
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