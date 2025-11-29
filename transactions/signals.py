from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transactions


@receiver(post_save, sender=Transactions)
def post_save_transaction(sender, instance, created, **kwargs):
    if created:
        # Logic to execute after a transaction is saved
        pass
