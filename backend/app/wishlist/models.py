import uuid
from sqlalchemy import ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime

class Wishlist(Base):
    __tablename__ = "wishlists"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    created_at: Mapped[CreatedAtCol]

    user: Mapped["User"] = relationship("User", back_populates="wishlist_items")
    product: Mapped["Product"] = relationship("Product", back_populates="wishlist_items")
