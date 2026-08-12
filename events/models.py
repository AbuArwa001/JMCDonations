from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Event Categories"
        
    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    story = models.TextField(help_text="Rich text: context on why this event matters, who the guest is, etc.")
    cover_image = models.ImageField(upload_to='events/covers/', blank=True, null=True)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    venue_name = models.CharField(max_length=255)
    venue_address = models.TextField(blank=True, null=True)
    venue_map_link = models.URLField(blank=True, null=True)
    guest_name = models.CharField(max_length=255, blank=True, null=True)
    guest_photo = models.ImageField(upload_to='events/guests/', blank=True, null=True)
    published = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-event_date', '-start_time']
        
    def __str__(self):
        return self.title

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='events/gallery/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
        
    def __str__(self):
        return f"Image for {self.event.title}"
