import uuid
from sqlalchemy import ForeignKey, Integer, String, Numeric, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime
from typing import List, Optional

class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(20))  # shipping, billing
    full_name: Mapped[str] = mapped_column(String(255))
    street: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(20))
    phone: Mapped[str] = mapped_column(String(20))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="addresses")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="shipping_address")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    guest_email: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, paid, processing, shipped, delivered, cancelled, returned
    subtotal: Mapped[float] = mapped_column(Numeric(10,2))
    discount: Mapped[float] = mapped_column(Numeric(10,2), default=0.0)
    shipping_cost: Mapped[float] = mapped_column(Numeric(10,2), default=0.0)
    total: Mapped[float] = mapped_column(Numeric(10,2))
    shipping_address_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    payment_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, success, failed, refunded
    created_at: Mapped[CreatedAtCol]
    updated_at: Mapped[datetime] = mapped_column(default=Mapped[CreatedAtCol], onupdate=datetime.utcnow)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="orders")
    shipping_address: Mapped[Optional[Address]] = relationship("Address", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")
    payments: Mapped[List["PaymentTransaction"]] = relationship("PaymentTransaction", back_populates="order")
    returns: Mapped[List["Return"]] = relationship("Return", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    size_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("product_sizes.id"), nullable=True)
    color_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("product_colors.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer)
    price_at_purchase: Mapped[float] = mapped_column(Numeric(10,2))

    order: Mapped[Order] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    size: Mapped[Optional["ProductSize"]] = relationship("ProductSize", back_populates="order_items")
    color: Mapped[Optional["ProductColor"]] = relationship("ProductColor", back_populates="order_items")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"))
    provider: Mapped[str] = mapped_column(String(50))  # "tbank"
    external_id: Mapped[Optional[str]] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Numeric(10,2))
    status: Mapped[str] = mapped_column(String(50))  # pending, success, failed
    response_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[CreatedAtCol]

    order: Mapped[Order] = relationship("Order", back_populates="payments")

class Return(Base):
    __tablename__ = "returns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(50), default="requested")  # requested, approved, received, refunded, rejected
    reason: Mapped[str] = mapped_column(String(255))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    items: Mapped[dict] = mapped_column(JSON)  # список id заказанных товаров и количество
    created_at: Mapped[CreatedAtCol]
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    order: Mapped[Order] = relationship("Order", back_populates="returns")
    #user: Mapped["User"] = relationship("User", back_populates="orders")  # если нужно
