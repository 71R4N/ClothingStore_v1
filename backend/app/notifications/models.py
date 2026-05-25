import uuid
from sqlalchemy import ForeignKey, String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(50))  # order_status, tryon_ready, return_update
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[CreatedAtCol]

    user: Mapped["User"] = relationship("User", back_populates="notifications")
