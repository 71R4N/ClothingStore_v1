from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class TryOnRequest(BaseModel):
    product_id: int
    person_image_url: str  # уже загруженное изображение (предполагаем, что загрузка отдельно)
    garment_image_url: str  # из каталога, можно брать главное фото продукта
    mask_image_url: Optional[str] = None

class TryOnResult(BaseModel):
    id: UUID
    status: str
    result_image_url: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: datetime

class TryOnSessionRead(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    product_id: int
    person_image_url: str
    garment_image_url: str
    status: str
    result_image_url: Optional[str]
    model_version: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    model_config = {"from_attributes": True}

class TryOnCreate(BaseModel):
    """Схема для создания новой сессии примерки"""
    user_id: Optional[UUID] = None
    product_id: int
    person_image_url: str
    garment_image_url: str
    mask_image_url: Optional[str] = None
    status: str = "queued"
