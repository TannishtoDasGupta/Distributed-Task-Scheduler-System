"""Celery application configuration."""
from celery import Celery

from ..config import settings

celery_app = Celery(
    "distributed_task_scheduler",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
    task_publish_retry=True,
    task_default_delivery_mode="persistent",
    broker_transport_options={"visibility_timeout": 3600},
)
