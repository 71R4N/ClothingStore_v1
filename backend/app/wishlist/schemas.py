from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.catalog.schemas import ProductVariantRead


class WishlistCreate(BaseModel):
    variant_id: int


class WishlistRead(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    variant_id: int
    created_at: datetime
    variant: Optional[ProductVariantRead] = None
    model_config = {"from_attributes": True}