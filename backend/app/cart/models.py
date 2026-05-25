import uuid
from sqlalchemy import ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from datetime import datetime
from typing import Optional

class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    size_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("product_sizes.id"), nullable=True)
    color_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("product_colors.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Связи
    user: Mapped[Optional["User"]] = relationship("User", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")
    size: Mapped[Optional["ProductSize"]] = relationship("ProductSize", back_populates="cart_items")
    color: Mapped[Optional["ProductColor"]] = relationship("ProductColor", back_populates="cart_items")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", "size_id", "color_id", name="uq_cart_user_product"),
    )
    