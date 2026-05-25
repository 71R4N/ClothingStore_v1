import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime
from typing import List, Optional

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    phone: Mapped[Optional[str]]
    created_at: Mapped[CreatedAtCol]
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(default="user")  # guest, user, admin

    # связи
    sessions: Mapped[List["UserSession"]] = relationship(back_populates="user")
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")
    wishlist_items: Mapped[List["Wishlist"]] = relationship(back_populates="user")
    cart_items: Mapped[List["CartItem"]] = relationship(back_populates="user")
    reviews: Mapped[List["Review"]] = relationship(back_populates="user")
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")
    tryon_sessions: Mapped[List["TryOnSession"]] = relationship(back_populates="user")

