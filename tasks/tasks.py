from datetime import timedelta

import celery.schedules
import sentry_sdk
from celery import signals
from django.conf import settings
from django.db.models import TextChoices
from sentry_sdk.integrations.celery import CeleryIntegration

from config.celery import app
from tasks.system_monitoring import update_task_monitor

class TaskFrequency(TextChoices):
    five_minutes = "five_minutes"
    daily = "daily"


SCHEDULES = {
    TaskFrequency.five_minutes: celery.schedules.schedule(run_every=timedelta(minutes=5)),
    TaskFrequency.daily: celery.schedules.crontab(minute=0, hour=7),
}

# Set up scheduled tasks
@app.on_after_finalize.connect
def schedule_tasks(sender, **kwargs):
    if settings.CELERY_TASK_ALWAYS_EAGER:
        return
    for task_frequency, tasks in SCHEDULED_TASKS.items():
        schedule = SCHEDULES[task_frequency]
        for task_name, task in tasks.items():
            sender.add_periodic_task(schedule, task.s(), name=task_name)


SCHEDULED_TASKS = {
    TaskFrequency.five_minutes: {
        "update_task_monitor": update_task_monitor,
    },
    TaskFrequency.daily: {},
}
# START_FEATURE sentry
# Sentry task monitoring auto-instrumentation
@signals.celeryd_init.connect
def init_sentry(**kwargs):
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[CeleryIntegration(monitor_beat_tasks=True)],
        )
# END_FEATURE sentry
