from datetime import datetime
from app.tryon.repositories import TryOnRepo
from app.tryon.schemas import TryOnRequest
from app.tryon.ml_wrapper import CatVTONClient
from app.tryon.exceptions import TryOnSessionNotFoundError
from app.tryon.models import TryOnSession
from typing import Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class TryOnService:
    def __init__(self, tryon_repo: TryOnRepo):
        self.tryon_repo = tryon_repo
        self.ml_client = CatVTONClient()

    async def create_session(
            self,
            user_id: Optional[UUID],
            data: TryOnRequest
    ) -> TryOnSession:
        session = TryOnSession(
            user_id=user_id,
            variant_id=data.variant_id,
            person_image_url=data.person_image_url,
            garment_image_url=data.garment_image_url,
            mask_image_url=data.mask_image_url,
            status="queued"
        )

        self.tryon_repo.session.add(session)
        await self.tryon_repo.session.commit()
        await self.tryon_repo.session.refresh(session)
        return session

    async def process_session(self, session_id: UUID) -> TryOnSession:
        logger.info(f"Processing try-on session {session_id}")
        session = await self.tryon_repo.read_by_id(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            raise TryOnSessionNotFoundError()
        # Обновляем статус
        session.status = "processing"
        await self.tryon_repo.session.commit()
        # Запускаем обработку
        start = datetime.utcnow()
        result = await self.ml_client.run_tryon(
            person_img_url=session.person_image_url,
            garment_img_url=session.garment_image_url,
            mask_img_url=session.mask_image_url
        )
        end = datetime.utcnow()
        duration = int((end - start).total_seconds() * 1000)
        # Обновляем результаты
        if result.get("error"):
            session.status = "failed"
            session.error_message = result["error"]
            logger.error(f"Try-on failed: {result['error']}")
        else:
            session.status = "completed"
            session.result_image_url = result["result_image_url"]
            logger.info(f"Try-on completed in {duration}ms")
        session.completed_at = end
        session.duration_ms = duration
        await self.tryon_repo.session.commit()

        return session

    async def get_session(self, session_id: UUID) -> TryOnSession:
        session = await self.tryon_repo.read_by_id(session_id)
        if not session:
            raise TryOnSessionNotFoundError()
        return session

    async def get_user_sessions(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 20
    ) -> list[TryOnSession]:
        return await self.tryon_repo.get_by_user(user_id, skip, limit)
