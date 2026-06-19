from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TryOnRequest(BaseModel):
    variant_id: int
    person_image_url: str
    garment_image_url: str
    mask_image_url: Optional[str] = None
    category: Optional[str] = "upper_body"


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
    variant_id: int
    person_image_url: str
    garment_image_url: str
    status: str
    result_image_url: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    model_config = {"from_attributes": True}


class TryOnCreate(BaseModel):
    user_id: Optional[UUID] = None
    variant_id: int
    person_image_url: str
    garment_image_url: str
    mask_image_url: Optional[str] = None
    status: str = "queued"
