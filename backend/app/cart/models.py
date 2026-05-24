from sqlalchemy import ForeignKey, Integer, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base
from datetime import datetime
import uuid

class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)  # для гостей
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    size_id: Mapped[int | None] = mapped_column(ForeignKey("product_sizes.id"), nullable=True)
    color_id: Mapped[int | None] = mapped_column(ForeignKey("product_colors.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
