from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JumaKhutba
from .views import KhutbaNotifyView
from firebase_admin import messaging
from .models import DeviceToken, NotificationLog

@receiver(post_save, sender=JumaKhutba)
def auto_notify_khutba(sender, instance, created, **kwargs):
    if created and instance.published:
        # Check if we should auto notify (we could check a setting, but for now we just notify on publish if it's new)
        tokens = list(DeviceToken.objects.values_list('fcm_token', flat=True))
        if tokens:
            title = f"Friday Khutba: {instance.title}"
            body = f"Join us this Friday. Imam: {instance.imam_name} at {instance.khutba_time.strftime('%I:%M %p')}"
            
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={
                    'type': 'khutba',
                    'khutba_id': str(instance.id),
                },
                tokens=tokens,
            )
            try:
                response = messaging.send_multicast(message)
                NotificationLog.objects.create(
                    title=title,
                    body=body,
                    related_khutba=instance,
                    recipient_count=response.success_count
                )
            except Exception:
                pass
