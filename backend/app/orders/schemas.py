from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.catalog.schemas import ProductVariantRead


class OrderItemBase(BaseModel):
    variant_id: int
    quantity: int
    price_at_purchase: float


class OrderItemRead(OrderItemBase):
    id: UUID
    variant: Optional[ProductVariantRead] = None
    model_config = {"from_attributes": True}


class OrderBase(BaseModel):
    guest_email: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemBase]


class OrderRead(OrderBase):
    id: UUID
    user_id: Optional[UUID]
    status: str
    total: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead] = []
    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str
