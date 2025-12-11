import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JMCDonations.settings')
app = Celery('JMCDonations')
app.config_from_object('JMCDonations.settings', namespace='CELERY')
app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run every hour
    sender.add_periodic_task(
        crontab(minute=0),  # At minute 0 of every hour
        close_expired_donations_task.s(),
        name='Close expired donations hourly'
    )
    
    # Run daily at midnight as backup
    sender.add_periodic_task(
        crontab(minute=0, hour=0),
        close_expired_donations_task.s(),
        name='Close expired donations daily'
    )

@app.task
def close_expired_donations_task():
    from django.core.management import call_command
    call_command('close_expired_donations')