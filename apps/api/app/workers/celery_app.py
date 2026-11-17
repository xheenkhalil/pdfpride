import os
from celery import Celery
from apps.api.app.core.config import settings

celery_app = Celery(
    "pdfpride_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["apps.api.app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,        # Hard timeout 5 minutes
    task_soft_time_limit=240,   # Soft timeout 4 minutes
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)
