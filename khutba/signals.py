from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JumaKhutba
from .views import KhutbaNotifyView
from firebase_admin import messaging
from .models import DeviceToken, NotificationLog

@receiver(post_save, sender=JumaKhutba)
def auto_notify_khutba(sender, instance, created, **kwargs):
    if created and instance.published:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        device_tokens = list(DeviceToken.objects.values_list('fcm_token', flat=True))
        user_tokens = list(User.objects.exclude(fcm_token__isnull=True).exclude(fcm_token='').values_list('fcm_token', flat=True))
        tokens = list(set(device_tokens + user_tokens))
        
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
                response = messaging.send_each_for_multicast(message)
                NotificationLog.objects.create(
                    title=title,
                    body=body,
                    related_khutba=instance,
                    recipient_count=response.success_count
                )
            except Exception:
                pass
