import os

from celery import Celery
from kombu.utils.json import register_type
from django.db.models import Model
from django.apps import apps

# Allow serialization of Django models
register_type(
    Model,
    "model",
    lambda o: [o._meta.label, o.pk],
    lambda o: apps.get_model(o[0]).objects.get(pk=o[1]),
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