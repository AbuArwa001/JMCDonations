from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transactions


@receiver(post_save, sender=Transactions)
def post_save_transaction(sender, instance, created, **kwargs):
    """
    Auto-close donation if it reaches target amount when a transaction is completed.
    """
    if instance.payment_status == "Completed":
        donation = instance.donation
        donation.check_and_close_if_funded()
