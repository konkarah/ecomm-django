# from django.http import JsonResponse
# from django.db import connection
# import redis
# from django.conf import settings

# def health_check(request):
#     """Health check endpoint for Docker/Kubernetes"""
#     health_status = {
#         'status': 'healthy',
#         'database': 'unknown',
#         'redis': 'unknown'
#     }
    
#     # Check database
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT 1")
#         health_status['database'] = 'healthy'
#     except Exception:
#         health_status['database'] = 'unhealthy'
#         health_status['status'] = 'unhealthy'
    
#     # Check Redis
#     try:
#         r = redis.from_url(settings.CELERY_BROKER_URL)
#         r.ping()
#         health_status['redis'] = 'healthy'
#     except Exception:
#         health_status['redis'] = 'unhealthy'
#         health_status['status'] = 'unhealthy'
    
#     status_code = 200 if health_status['status'] == 'healthy' else 503
#     return JsonResponse(health_status, status=status_code)

# ecommerce_api/celery.py
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