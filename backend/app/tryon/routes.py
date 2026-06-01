from fastapi import APIRouter, Depends, UploadFile, File, Form
from worker.tasks.tryon import process_tryon_session
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
    person_image_url = "https://i.pinimg.com/1200x/4e/ce/68/4ece689d3f8a086a7d81e31b56aa704d.jpg"#"https://images.unsplash.com/photo-1666358080289-2401fbdd53cf?q=80&w=1170&auto=format&fit=crop"
    garment_image_url = "https://i.pinimg.com/1200x/d7/32/9b/d7329baef71fce8dea8eec58ce7e950b.jpg"#"https://images.unsplash.com/photo-1596755094514-f87e34085b2c?q=80&w=688&auto=format&fit=crop" # f"https://example.com/products/{product_id}/main.jpg"  # нужно получать из каталога
    request_data = TryOnRequest(
        product_id=product_id,
        person_image_url=person_image_url,
        garment_image_url=garment_image_url
    )
    user_id = str(current_user.id) if current_user else None
    session = await tryon_svc.create_session(user_id, request_data)
    process_tryon_session.delay(str(session.id))  # запуск в фоне
    return session

@router.get("/sessions/{session_id}", response_model=TryOnSessionRead)
async def get_session(session_id: UUID, tryon_svc: TryOnServiceDep):
    return await tryon_svc.get_session(session_id)

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
