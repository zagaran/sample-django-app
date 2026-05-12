from django.utils import timezone
from common.models import User
from config.celery import app


@app.task
def update_task_monitor():
    # Auto-instrumented cron monitor hook for worker server downtime detection
    # Just run any query to check db access
    User.objects.exists()