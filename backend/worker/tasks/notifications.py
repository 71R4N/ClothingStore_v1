from worker.celery_app import celery
from app.notifications.services import NotificationService
from app.notifications.repositories import NotificationRepo
from app.core.database import AsyncSessionLocal
import asyncio

@celery.task
def send_notification(user_id: str, type: str, title: str, message: str):
    async def _run():
        async with AsyncSessionLocal() as session:
            service = NotificationService(NotificationRepo(session))
            await service.send(user_id, type, title, message)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run())
    