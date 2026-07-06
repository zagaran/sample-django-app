import os

import django.db
from celery import Celery
from django.conf import settings
from kombu.utils.json import register_type
from django.db.models import Model
from django.apps import apps


def safe_deserialize_model(o):
    # If outside request context, clean up unusable db connections before attempting to fetch instance
    if not settings.CELERY_TASK_ALWAYS_EAGER:
        django.db.close_old_connections()
    return apps.get_model(o[0]).objects.get(pk=o[1])

# Allow serialization of django models by pk
register_type(
    Model,
    "model",
    lambda o: [o._meta.label, o.pk],
    safe_deserialize_model,
)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery("sample-django-app")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()