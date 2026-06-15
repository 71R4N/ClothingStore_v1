from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class PaymentCreate(BaseModel):
    order_id: UUID


class PaymentRead(BaseModel):
    id: UUID
    order_id: UUID
    yookassa_payment_id: Optional[str] = None
    amount: float
    currency: str = "RUB"
    status: str
    payment_method: Optional[str] = None
    is_test: bool = False
    confirmation_url: Optional[str] = None
    payment_url: Optional[str] = None
    error_message: Optional[str] = None
    cancellation_reason: Optional[str] = None
    cancellation_party: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentInitiateResponse(BaseModel):
    payment_id: UUID
    yookassa_payment_id: str
    confirmation_url: str
    status: str
    is_test: bool = False


class PaymentPollResponse(BaseModel):
    id: UUID
    order_id: UUID
    status: str
    payment_method: Optional[str] = None
    amount: float
    is_test: bool = False
    updated_at: datetime

    model_config = {"from_attributes": True}
