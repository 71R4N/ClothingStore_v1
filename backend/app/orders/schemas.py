from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.catalog.schemas import ProductVariantRead


class OrderItemBase(BaseModel):
    variant_id: int
    quantity: int = Field(gt=0)
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
    pass


class OrderRead(OrderBase):
    id: UUID
    user_id: Optional[UUID]
    status: str
    total: float
    has_returns: bool = False
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead] = Field(default_factory=list)
    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str