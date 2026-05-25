import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime
from typing import Optional

class TryOnSession(Base):
    __tablename__ = "tryon_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    person_image_url: Mapped[str] = mapped_column(String(500))  # URL загруженной фотографии пользователя
    garment_image_url: Mapped[str] = mapped_column(String(500))  # URL изображения одежды из каталога
    mask_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    result_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="queued")  # queued, processing, completed, failed
    model_version: Mapped[Optional[str]] = mapped_column(String(50), default="CatVTON-v1")
    model_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[CreatedAtCol]
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="tryon_sessions")
    product: Mapped["Product"] = relationship("Product", back_populates="tryon_sessions")