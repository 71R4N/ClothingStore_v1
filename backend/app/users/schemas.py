from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    is_active: bool
    role: str
    created_at: datetime
    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    