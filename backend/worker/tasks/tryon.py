from worker.celery_app import celery
from app.tryon.services import TryOnService
from app.tryon.repositories import TryOnRepo
from app.core.database import AsyncSessionLocal
import asyncio

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def process_tryon_session(self, session_id: str):
    async def _run():
        async with AsyncSessionLocal() as session:
            repo = TryOnRepo(session)
            service = TryOnService(repo)
            try:
                await service.process_session(session_id)
            except Exception as e:
                # обновить статус failed
                session_obj = await repo.read_by_id(session_id)
                if session_obj:
                    session_obj.status = "failed"
                    session_obj.error_message = str(e)
                    await repo.update(session_obj, session_id, exclude_unset=False)
                raise self.retry(exc=e)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run())
