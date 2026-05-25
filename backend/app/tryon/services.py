import uuid
from datetime import datetime
from app.tryon.repositories import TryOnRepo
from app.tryon.schemas import TryOnRequest
from app.tryon.ml_wrapper import CatVTONClient
from app.tryon.exceptions import TryOnSessionNotFoundError, TryOnProcessingError
from typing import Optional

from app.tryon.models import TryOnSession


class TryOnService:
    def __init__(self, tryon_repo: TryOnRepo):
        self.tryon_repo = tryon_repo
        self.ml_client = CatVTONClient()

    async def create_session(self, user_id: Optional[str], data: TryOnRequest) -> TryOnSession:
        session_data = {
            "user_id": user_id,
            "product_id": data.product_id,
            "person_image_url": data.person_image_url,
            "garment_image_url": data.garment_image_url,
            "mask_image_url": data.mask_image_url,
            "status": "queued"
        }
        session_id = await self.tryon_repo.create(TryOnCreate(**session_data))
        return await self.tryon_repo.read_by_id(session_id)

    async def process_session(self, session_id: str) -> TryOnSession:
        session = await self.tryon_repo.read_by_id(session_id)
        if not session:
            raise TryOnSessionNotFoundError()

        # Обновляем статус на processing
        session.status = "processing"
        await self.tryon_repo.update(session, session_id, exclude_unset=False)

        # Запуск ML
        start = datetime.utcnow()
        result = await self.ml_client.run_tryon(
            person_img_url=session.person_image_url,
            garment_img_url=session.garment_image_url,
            mask_img_url=session.mask_image_url
        )
        end = datetime.utcnow()
        duration = int((end - start).total_seconds() * 1000)

        if result.get("error"):
            session.status = "failed"
            session.error_message = result["error"]
        else:
            session.status = "completed"
            session.result_image_url = result["result_image_url"]
        session.completed_at = end
        session.duration_ms = duration
        await self.tryon_repo.update(session, session_id, exclude_unset=False)
        return session

    async def get_session(self, session_id: str) -> TryOnSession:
        session = await self.tryon_repo.read_by_id(session_id)
        if not session:
            raise TryOnSessionNotFoundError()
        return session

    async def get_user_sessions(self, user_id: str, skip: int = 0, limit: int = 20):
        # необходимо добавить метод в репозиторий
        return await self.tryon_repo.get_by_user(user_id, skip, limit)
