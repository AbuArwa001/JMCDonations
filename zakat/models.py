from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class NisabRate(models.Model):
    gold_price_per_gram = models.DecimalField(max_digits=10, decimal_places=2)
    silver_price_per_gram = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="KES")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'gold_price_per_gram': 0,
                'silver_price_per_gram': 0,
                'currency': 'KES'
            }
        )
        return obj

    def __str__(self):
        return f"Nisab Rate ({self.currency})"
