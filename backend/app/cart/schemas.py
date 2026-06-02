from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.catalog.schemas import ProductVariantRead


class CartItemBase(BaseModel):
    variant_id: int  # ← заменено!
    quantity: int = Field(gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemRead(CartItemBase):
    id: UUID
    user_id: Optional[UUID]
    session_id: Optional[str]
    added_at: datetime
    variant: Optional[ProductVariantRead] = None  # ← подгружаем вариант
    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    items: List[CartItemRead]
    total: float