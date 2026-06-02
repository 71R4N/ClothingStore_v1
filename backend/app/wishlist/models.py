import uuid
from typing import Optional
from sqlalchemy import ForeignKey, Integer, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol


class Wishlist(Base):
    __tablename__ = "wishlists"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"))
    created_at: Mapped[CreatedAtCol]

    user: Mapped[Optional["User"]] = relationship("User", back_populates="wishlist_items")
    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="wishlist_items")

    __table_args__ = (
        UniqueConstraint('user_id', 'variant_id', name='unique_user_wishlist', postgresql_nulls_not_distinct=True),
        UniqueConstraint('session_id', 'variant_id', name='unique_session_wishlist', postgresql_nulls_not_distinct=True),
    )