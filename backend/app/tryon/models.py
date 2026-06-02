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
    variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"))
    person_image_url: Mapped[str] = mapped_column(String(500))
    garment_image_url: Mapped[str] = mapped_column(String(500))
    mask_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    result_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="queued")
    created_at: Mapped[CreatedAtCol]
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="tryon_sessions")
    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="tryon_sessions")
