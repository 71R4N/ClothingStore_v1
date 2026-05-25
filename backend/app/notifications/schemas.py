from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class NotificationRead(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    model_config = {"from_attributes": True}
    