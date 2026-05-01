from django.db import models

class ContentType(models.TextChoices):
    DARSA = 'DARSA', 'Darsa'
    DUA = 'DUA', 'Dua'
    INSPIRATION = 'INSPIRATION', 'Daily Inspiration'
    KHUTBA = 'KHUTBA', 'Juma Khutba'

class CommunityContent(models.Model):
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    title = models.CharField(max_length=255)
    body = models.TextField()
    author_or_sheikh = models.CharField(max_length=255, blank=True, null=True)
    scheduled_for = models.DateTimeField(blank=True, null=True, help_text="When should this be shown? (e.g., Darsa time)")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"[{self.get_content_type_display()}] {self.title}"
