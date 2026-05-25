import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    rating: Mapped[int] = mapped_column(Integer)  # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[CreatedAtCol]
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship("User", back_populates="reviews")
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
