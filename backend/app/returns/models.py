import uuid
import enum
from sqlalchemy import (
    ForeignKey, String, Numeric, Text,
    Enum as SAEnum, DateTime, JSON, Integer, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime
from typing import List, Optional


class ReturnStatus(str, enum.Enum):
    """Статусы заявки на возврат."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ReturnReasonType(str, enum.Enum):
    """Причины возврата товара."""
    DEFECTIVE = "defective"
    WRONG_SIZE = "wrong_size"
    WRONG_COLOR = "wrong_color"
    CHANGED_MIND = "changed_mind"
    OTHER = "other"


class Return(Base):
    """Модель заявки на возврат товаров."""
    __tablename__ = "returns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    guest_email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    status: Mapped[ReturnStatus] = mapped_column(
        SAEnum(ReturnStatus, name="return_status_enum", create_constraint=True),
        default=ReturnStatus.PENDING, nullable=False, index=True
    )
    reason_type: Mapped[ReturnReasonType] = mapped_column(
        SAEnum(ReturnReasonType, name="return_reason_enum", create_constraint=True),
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False), nullable=False
    )
    refund_payment_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[CreatedAtCol]
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Связи
    order: Mapped["Order"] = relationship("Order", back_populates="returns")
    items: Mapped[List["ReturnItem"]] = relationship(
        "ReturnItem",
        back_populates="return_request",
        cascade="all, delete-orphan"
    )
    resolver: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[resolved_by]
    )

    __table_args__ = (
        Index("ix_returns_order_status", "order_id", "status"),
    )


class ReturnItem(Base):
    """Модель позиции возврата (конкретный товар из заказа)."""
    __tablename__ = "return_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    return_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("returns.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    order_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    variant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product_variants.id", ondelete="SET NULL"),
        nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    refund_amount: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False), nullable=False
    )
    photos: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[CreatedAtCol]

    # Связи
    return_request: Mapped["Return"] = relationship(
        "Return", back_populates="items"
    )
    order_item: Mapped["OrderItem"] = relationship(
        "OrderItem", back_populates="return_items"
    )
    variant: Mapped[Optional["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="return_items"
    )
