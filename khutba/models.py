from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class JumaKhutba(models.Model):
    khutba_date = models.DateField()
    khutba_time = models.TimeField()
    imam_name = models.CharField(max_length=200)
    imam_photo = models.ImageField(upload_to='khutba/imams/', blank=True, null=True)
    title = models.CharField(max_length=255)
    topic_summary = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-khutba_date', '-khutba_time']
        
    def __str__(self):
        return f"{self.title} by {self.imam_name} on {self.khutba_date}"

class DeviceToken(models.Model):
    fcm_token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=50, blank=True, null=True) # e.g. ios, android, web
    registered_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.platform} token ending in {self.fcm_token[-5:]}"

class NotificationLog(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    related_khutba = models.ForeignKey(JumaKhutba, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-sent_at']
        
    def __str__(self):
        return f"Notification: {self.title} sent at {self.sent_at}"
