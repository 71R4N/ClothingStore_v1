import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, Numeric, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, CreatedAtCol
from typing import List, Optional
from app.cart.models import CartItem
from app.orders.models import OrderItem
from app.wishlist.models import Wishlist
from app.tryon.models import TryOnSession


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
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    brand: Mapped[Optional[str]] = mapped_column(String(255))
    brand_logo: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[CreatedAtCol]

    category: Mapped[Category] = relationship("Category", back_populates="products")
    sizes: Mapped[List["ProductSize"]] = relationship(
        "ProductSize", back_populates="product", cascade="all, delete-orphan"
    )
    colors: Mapped[List["ProductColor"]] = relationship(
        "ProductColor", back_populates="product", cascade="all, delete-orphan"
    )
    variants: Mapped[List["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan"
    )


class ProductSize(Base):
    __tablename__ = "product_sizes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    size_label: Mapped[str] = mapped_column(String(50))
    chest_cm: Mapped[Optional[str]] = mapped_column(String(50))
    waist_cm: Mapped[Optional[str]] = mapped_column(String(50))
    hips_cm: Mapped[Optional[str]] = mapped_column(String(50))
    height_cm: Mapped[Optional[str]] = mapped_column(String(50))

    product: Mapped[Product] = relationship("Product", back_populates="sizes")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="size")


class ProductColor(Base):
    __tablename__ = "product_colors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    color_name: Mapped[str] = mapped_column(String(100))
    color_hex: Mapped[str] = mapped_column(String(7))

    product: Mapped[Product] = relationship("Product", back_populates="colors")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="color")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    color_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_colors.id", ondelete="CASCADE"))
    size_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_sizes.id", ondelete="CASCADE"))
    sku: Mapped[str] = mapped_column(String(100), unique=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))
    # ✅ Изображения варианта хранятся здесь
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    attributes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    color: Mapped["ProductColor"] = relationship("ProductColor", back_populates="variants")
    size: Mapped["ProductSize"] = relationship("ProductSize", back_populates="variants")
    cart_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="variant")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="variant")
    wishlist_items: Mapped[List["Wishlist"]] = relationship("Wishlist", back_populates="variant")
    tryon_sessions: Mapped[List["TryOnSession"]] = relationship("TryOnSession", back_populates="variant")
