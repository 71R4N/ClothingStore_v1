from celery import Celery
from app.core.database import AsyncSessionLocal
from app.tryon.services import TryOnService
from app.tryon.repositories import TryOnRepo
import asyncio
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    'tryon_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)


@celery_app.task(name='process_tryon_session')
def process_tryon_session(session_id: str):
    """Celery задача для обработки try-on сессии"""
    logger.info(f"Starting Celery task for session {session_id}")

    asyncio.run(_process_session_async(session_id))


async def _process_session_async(session_id: str):
    """Async обертка для обработки сессии"""
    from uuid import UUID

    async with AsyncSessionLocal() as session:
        tryon_repo = TryOnRepo(session)
        tryon_service = TryOnService(tryon_repo)

        try:
            await tryon_service.process_session(UUID(session_id))
            logger.info(f"Celery task completed for session {session_id}")
        except Exception as e:
            logger.error(f"Celery task failed for session {session_id}: {e}")
            raise
