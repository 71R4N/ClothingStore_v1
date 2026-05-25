from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class WishlistCreate(BaseModel):
    product_id: int

class WishlistRead(BaseModel):
    id: UUID
    user_id: UUID
    product_id: int
    created_at: datetime
    model_config = {"from_attributes": True}
    