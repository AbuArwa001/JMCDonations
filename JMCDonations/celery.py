# JMCDonations/celery.py
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JMCDonations.settings')

app = Celery('JMCDonations')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Optional: Configure beat schedule here if not using database scheduler
app.conf.beat_schedule = {
    'close-expired-donations-hourly': {
        'task': 'donations.tasks.close_expired_donations_task',
        'schedule': 3600.0,  # Every hour
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')