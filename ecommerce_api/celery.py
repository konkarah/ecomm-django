import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')

app = Celery('ecommerce_api', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
BROKER_URL = "redis://localhost:6379"
broker_url = "redis://localhost:6379"
app.conf.broker_url = BROKER_URL
CELERY_BROKER_URL = BROKER_URL
app.conf.beat_schedule = {

"""'
Test celery worker
send_admin_message': {
    'task': 'home.tasks.test_task',
    'schedule': 3,
},"""
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')