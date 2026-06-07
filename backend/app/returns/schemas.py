from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class ReturnStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ReturnReasonEnum(str, Enum):
    DEFECTIVE = "defective"
    WRONG_SIZE = "wrong_size"
    WRONG_COLOR = "wrong_color"
    CHANGED_MIND = "changed_mind"
    OTHER = "other"


class ReturnCreate(BaseModel):
    """Схема для создания заявки на возврат одного товара."""
    order_id: UUID
    order_item_id: UUID
    quantity: int = Field(gt=0, description="Количество к возврату")
    reason_type: ReturnReasonEnum
    description: Optional[str] = Field(None, max_length=1000)
    photos: List[str] = Field(default_factory=list)

    @field_validator("photos")
    @classmethod
    def validate_photos(cls, v: List[str]) -> List[str]:
        if len(v) > 5:
            raise ValueError("Maximum 5 photos per return item")
        for url in v:
            if not url.startswith("/static/uploads/"):
                raise ValueError(f"Invalid photo URL: {url}")
        return v


class ReturnRead(BaseModel):
    """Схема для чтения заявки на возврат."""
    id: UUID
    order_id: UUID
    order_item_id: UUID
    user_id: Optional[UUID] = None
    guest_email: Optional[str] = None
    status: str
    reason_type: str
    description: Optional[str] = None
    quantity: int
    refund_amount: float
    photos: List[str] = Field(default_factory=list)
    refund_payment_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    # Вложенная информация о товаре (вычисляется из order_item)
    product_name: Optional[str] = None
    size_label: Optional[str] = None
    color_name: Optional[str] = None
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class ReturnActionRequest(BaseModel):
    """Схема для административного действия (approve/reject)."""
    action: str = Field(pattern="^(approve|reject)$")
    rejection_reason: Optional[str] = Field(None, max_length=500)


class ReturnListResponse(BaseModel):
    """Список возвратов с пагинацией."""
    items: List[ReturnRead]
    total: int
