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
from typing import Optional


class ReturnStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ReturnReasonType(str, enum.Enum):
    DEFECTIVE = "defective"
    WRONG_SIZE = "wrong_size"
    WRONG_COLOR = "wrong_color"
    CHANGED_MIND = "changed_mind"
    OTHER = "other"


class Return(Base):
    __tablename__ = "returns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    order_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("order_items.id", ondelete="CASCADE"),
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

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    refund_amount: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False), nullable=False
    )
    photos: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
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

    order: Mapped["Order"] = relationship("Order", back_populates="returns")
    order_item: Mapped["OrderItem"] = relationship(
        "OrderItem", back_populates="returns"
    )
    resolver: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[resolved_by]
    )

    __table_args__ = (
        Index("ix_returns_order_status", "order_id", "status"),
        Index("ix_returns_order_item_status", "order_item_id", "status"),
    )

    @property
    def total_amount(self) -> float:
        return self.refund_amount

    @property
    def product_name(self) -> Optional[str]:
        if self.order_item and self.order_item.variant and self.order_item.variant.product:
            return self.order_item.variant.product.name
        return None

    @property
    def size_label(self) -> Optional[str]:
        if self.order_item and self.order_item.variant and self.order_item.variant.size:
            return self.order_item.variant.size.size_label
        return None

    @property
    def color_name(self) -> Optional[str]:
        if self.order_item and self.order_item.variant and self.order_item.variant.color:
            return self.order_item.variant.color.color_name
        return None

    @property
    def image_url(self) -> Optional[str]:
        if self.order_item and self.order_item.variant:
            return self.order_item.variant.image_url
        return None


class ReturnItem(Base):
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

    order_item: Mapped["OrderItem"] = relationship(
        "OrderItem", back_populates="return_items"
    )
    variant: Mapped[Optional["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="return_items"
    )

    @property
    def product_name(self) -> Optional[str]:
        if self.variant and self.variant.product:
            return self.variant.product.name
        return None

    @property
    def size_label(self) -> Optional[str]:
        if self.variant and self.variant.size:
            return self.variant.size.size_label
        return None

    @property
    def color_name(self) -> Optional[str]:
        if self.variant and self.variant.color:
            return self.variant.color.color_name
        return None

    @property
    def image_url(self) -> Optional[str]:
        if self.variant:
            return self.variant.image_url
        return None
