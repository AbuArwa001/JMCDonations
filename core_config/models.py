from django.db import models

class AppFeature(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., 'prayer_times', 'daily_inspiration'")
    is_active = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"
