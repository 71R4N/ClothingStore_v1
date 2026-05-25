from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class CartItemBase(BaseModel):
    product_id: int
    size_id: Optional[int] = None
    color_id: Optional[int] = None
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
    model_config = {"from_attributes": True}

class CartResponse(BaseModel):
    items: list[CartItemRead]
    total: float  # можно вычислять на бэке
    