import uuid
import enum
from sqlalchemy import ForeignKey, String, Numeric, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime
from typing import Optional


class PaymentStatus(str, enum.Enum):
    """Статусы платежа ЮKassa."""
    PENDING = "pending"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"


class PaymentMethod(str, enum.Enum):
    """Методы оплаты ЮKassa."""
    BANK_CARD = "bank_card"
    YOO_MONEY = "yoo_money"
    SBP = "sbp"
    TINKOFF_BANK = "tinkoff_bank"
    SBERBANK = "sberbank"
    ALFABANK = "alfabank"


class Payment(Base):
    """Модель платежа."""
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    yookassa_payment_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )
    amount: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="RUB"
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus, name="payment_status_enum", create_constraint=True),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True
    )
    payment_method: Mapped[Optional[PaymentMethod]] = mapped_column(
        SAEnum(PaymentMethod, name="payment_method_enum", create_constraint=True),
        nullable=True
    )
    is_test: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    confirmation_url: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True
    )
    payment_url: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    cancellation_party: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    created_at: Mapped[CreatedAtCol]
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    order: Mapped["Order"] = relationship("Order", back_populates="payments")
