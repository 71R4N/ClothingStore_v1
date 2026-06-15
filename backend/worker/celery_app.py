from celery import Celery
from app.core.config import settings

celery = Celery(
    "catvton_shop",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "worker.tasks.tryon",
        "worker.tasks.cleanup",
        "worker.tasks.returns",
    ]
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

celery.conf.beat_schedule = {
    "cleanup-old-tryon-results": {
        "task": "worker.tasks.cleanup.cleanup_old_tryon_results",
        "schedule": 3600.0,
        "args": (24,),
    },
}