import uuid
import enum
from sqlalchemy import ForeignKey, String, Numeric, Enum as SAEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime
from typing import List, Optional


class OrderStatus(str, enum.Enum):
    PENDING = "pending"           # Ожидает оплаты
    PROCESSING = "processing"     # Оплачен, собирается на складе
    SHIPPED = "shipped"           # Передан в службу доставки
    DELIVERED = "delivered"       # Доставлен клиенту
    CANCELLED = "cancelled"       # Отменён


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    guest_email: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status_enum", create_constraint=True),
        default=OrderStatus.PENDING,
        nullable=False
    )

    street: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    total: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))
    created_at: Mapped[CreatedAtCol]
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="order", cascade="all, delete-orphan"
    )

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE")
    )
    variant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product_variants.id")
    )
    quantity: Mapped[int] = mapped_column(Integer)
    price_at_purchase: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))

    order: Mapped[Order] = relationship("Order", back_populates="items")
    variant: Mapped[Optional["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="order_items"
    )