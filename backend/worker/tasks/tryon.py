# backend/worker/tasks/tryon.py
import asyncio
import logging
from uuid import UUID
from celery import shared_task
from app.core.database import AsyncSessionLocal
from app.tryon.services import TryOnService
from app.tryon.repositories import TryOnRepo

logger = logging.getLogger(__name__)


@shared_task(name='process_tryon_session', bind=True, max_retries=3)
def process_tryon_session(self, session_id: str):
    """Celery task for processing try-on session with isolated event loop"""
    logger.info(f"Starting Celery task for session {session_id}")

    # Создаём новый event loop для изоляции от контекста Celery
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_process_session_async(session_id))
    except Exception as e:
        logger.error(f"Task failed for session {session_id}: {e}")
        raise self.retry(exc=e, countdown=60)
    finally:
        loop.close()


async def _process_session_async(session_id: str):
    async with AsyncSessionLocal() as session:
        tryon_repo = TryOnRepo(session)
        tryon_service = TryOnService(tryon_repo)
        await tryon_service.process_session(UUID(session_id))
        logger.info(f"Try-on session {session_id} processed successfully")
