from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from decimal import Decimal

class CartItemBase(BaseModel):
    product_id: int
    size_id: Optional[int] = None
    color_id: Optional[int] = None
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(CartItemBase):
    id: UUID
    added_at: str
    # Дополнительно можем подгрузить информацию о товаре
    product_name: Optional[str] = None
    product_price: Optional[Decimal] = None
    size_label: Optional[str] = None
    color_name: Optional[str] = None
    image_url: Optional[str] = None

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_items: int
    subtotal: Decimal
    