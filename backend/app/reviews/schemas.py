from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class ReviewRead(BaseModel):
    id: UUID
    user_id: UUID
    product_id: int
    rating: int
    comment: Optional[str]
    is_verified: bool
    created_at: datetime
    helpful_count: int
    model_config = {"from_attributes": True}
    