import logging
from datetime import timedelta

import celery.schedules
from django.conf import settings
from django.db.models import TextChoices

from config.celery import app

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


# TODO: Delete me
@app.task
def sample_task():
    logging.info("Sample task running")


SCHEDULED_TASKS = {
    TaskFrequency.five_minutes: {sample_task},
    TaskFrequency.daily: {},
}
