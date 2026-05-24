from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from backend.app.users.models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class RegisterUserSchema(UserBase):
    password: str

class UpdateUserSchema(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None

class ResponseUserSchema(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    role: UserRole

    class Config:
        from_attributes = True
