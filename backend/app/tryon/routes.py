from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.tryon.schemas import TryOnRequest, TryOnSessionRead
from app.tryon.dependencies import TryOnServiceDep
from app.tryon.services import TryOnService
from app.auth.dependencies import CurrentUserDep
from typing import Annotated, Optional
from uuid import UUID

from app.core.exceptions import ForbiddenException

router = APIRouter(prefix="/try-on", tags=["tryon"])

@router.post("/sessions", response_model=TryOnSessionRead, status_code=201)
async def create_tryon(
    tryon_svc: TryOnServiceDep,
    current_user: CurrentUserDep,
    product_id: int = Form(...),
    person_image: UploadFile = File(...)  # предполагаем загрузку файла, но для простоты URL
):
    # Здесь должен быть код загрузки изображения в S3/локальное хранилище и получение URL.
    # Для MVP: просто передадим URL заглушки.
    person_image_url = "https://example.com/user_photo.jpg"
    garment_image_url = f"https://example.com/products/{product_id}/main.jpg"  # нужно получать из каталога
    request_data = TryOnRequest(
        product_id=product_id,
        person_image_url=person_image_url,
        garment_image_url=garment_image_url
    )
    user_id = str(current_user.id) if current_user else None
    session = await tryon_svc.create_session(user_id, request_data)
    # Запускаем обработку в фоне через Celery (будет позже)
    # task = process_tryon_session.delay(str(session.id))
    return session

@router.get("/sessions/{session_id}", response_model=TryOnSessionRead)
async def get_session(session_id: UUID, tryon_svc: TryOnServiceDep):
    return await tryon_svc.get_session(str(session_id))

@router.get("/sessions", response_model=list[TryOnSessionRead])
async def list_sessions(
    tryon_svc: TryOnServiceDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 20
):
    if not current_user:
        raise ForbiddenException()
    return await tryon_svc.get_user_sessions(str(current_user.id), skip, limit)
