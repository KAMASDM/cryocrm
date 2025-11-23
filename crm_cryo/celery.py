import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_cryo.settings')

app = Celery('crm_cryo')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'send-daily-appointment-reminders': {
        'task': 'communications.tasks.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    'send-package-expiry-warnings': {
        'task': 'communications.tasks.send_package_expiry_warnings',
        'schedule': crontab(hour=10, minute=0),  # Every day at 10 AM
    },
    'send-birthday-greetings': {
        'task': 'communications.tasks.send_birthday_greetings',
        'schedule': crontab(hour=8, minute=0),  # Every day at 8 AM
    },
    'process-scheduled-emails': {
        'task': 'communications.tasks.process_scheduled_emails',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
