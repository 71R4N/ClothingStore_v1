import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, Numeric, Boolean, DateTime, JSON, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base, CreatedAtCol
from datetime import datetime
from typing import List, Optional

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], backref="children")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    old_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    brand: Mapped[Optional[str]] = mapped_column(String(255))
    sku: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[CreatedAtCol]

    category: Mapped[Category] = relationship("Category", back_populates="products")
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="product")
    sizes: Mapped[List["ProductSize"]] = relationship("ProductSize", back_populates="product")
    colors: Mapped[List["ProductColor"]] = relationship("ProductColor", back_populates="product")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="product")
    cart_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="product")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")
    wishlist_items: Mapped[List["Wishlist"]] = relationship("Wishlist", back_populates="product")
    tryon_sessions: Mapped[List["TryOnSession"]] = relationship("TryOnSession", back_populates="product")

class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    url: Mapped[str] = mapped_column(String(500))
    alt_text: Mapped[Optional[str]] = mapped_column(String(255))
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship("Product", back_populates="images")

class ProductSize(Base):
    __tablename__ = "product_sizes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    size_label: Mapped[str] = mapped_column(String(50))
    chest_cm: Mapped[Optional[str]] = mapped_column(String(50))
    waist_cm: Mapped[Optional[str]] = mapped_column(String(50))
    hips_cm: Mapped[Optional[str]] = mapped_column(String(50))
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    sku_variant: Mapped[str] = mapped_column(String(100), unique=True)

    product: Mapped[Product] = relationship("Product", back_populates="sizes")
    cart_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="size")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="size")

class SizeChart(Base):
    __tablename__ = "size_charts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(10))  # EU, US, RU
    size_mapping: Mapped[dict] = mapped_column(JSON)

class ProductColor(Base):
    __tablename__ = "product_colors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    color_name: Mapped[str] = mapped_column(String(100))
    color_hex: Mapped[str] = mapped_column(String(7))

    product: Mapped[Product] = relationship("Product", back_populates="colors")
    cart_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="color")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="color")
