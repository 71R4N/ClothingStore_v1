from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Address
class AddressBase(BaseModel):
    type: str
    full_name: str
    street: str
    city: str
    postal_code: str
    phone: str
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressRead(AddressBase):
    id: UUID
    user_id: UUID
    model_config = {"from_attributes": True}

# OrderItem
class OrderItemBase(BaseModel):
    product_id: int
    size_id: Optional[int] = None
    color_id: Optional[int] = None
    quantity: int
    price_at_purchase: float

class OrderItemRead(OrderItemBase):
    id: UUID
    model_config = {"from_attributes": True}

# Order
class OrderBase(BaseModel):
    guest_email: Optional[str] = None
    shipping_address_id: Optional[UUID] = None
    payment_method: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemBase]
    # можно также передать адрес для создания нового, но упростим

class OrderRead(OrderBase):
    id: UUID
    user_id: Optional[UUID]
    status: str
    subtotal: float
    discount: float
    shipping_cost: float
    total: float
    payment_status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead] = []
    model_config = {"from_attributes": True}

class OrderStatusUpdate(BaseModel):
    status: str

class PaymentTransactionRead(BaseModel):
    id: UUID
    order_id: UUID
    provider: str
    external_id: Optional[str]
    amount: float
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}

class ReturnRequest(BaseModel):
    reason: str
    comment: Optional[str] = None
    items: dict  # {order_item_id: quantity}

class ReturnRead(BaseModel):
    id: UUID
    order_id: UUID
    user_id: UUID
    status: str
    reason: str
    comment: Optional[str]
    items: dict
    created_at: datetime
    resolved_at: Optional[datetime]
    model_config = {"from_attributes": True}
    