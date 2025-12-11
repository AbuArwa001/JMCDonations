import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JMCDonations.settings')

app = Celery('JMCDonations')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configure beat schedule
app.conf.beat_schedule = {
    'close-expired-donations-hourly': {
        'task': 'donations.tasks.close_expired_donations_task',
        'schedule': crontab(minute=0),  # Run at the beginning of every hour
        'args': (),
    },
    'check-expiring-donations-daily': {
        'task': 'donations.tasks.check_and_notify_expiring_donations',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
        'args': (),
    },
    'donation-health-check': {
        'task': 'donations.tasks.donation_health_check',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes
        'args': (),
    },
}

app.conf.timezone = 'Africa/Nairobi'