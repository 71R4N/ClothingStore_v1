from celery import Celery
from app.core.config import settings

celery = Celery(
    "catvton_shop",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["worker.tasks.tryon", "worker.tasks.notifications"]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
