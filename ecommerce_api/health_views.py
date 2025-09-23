import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')

app = Celery('ecommerce_api')

# Configure Celery using settings from Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Force eager execution to override any broker connection attempts
app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True,
)

# Load task modules from all registered Django app configs
app.autodiscover_tasks()