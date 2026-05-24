from sqlalchemy import String, Text, ForeignKey, Integer, DECIMAL, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base, created_at, str_uniq
from typing import List, Optional

class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str_uniq] = mapped_column(String(120), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    # relationship для иерархии
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side="Category.id", backref="children")

class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str_uniq] = mapped_column(String(220), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(10,2), nullable=False)
    old_price: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(10,2))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    brand: Mapped[Optional[str]] = mapped_column(String(100))
    sku: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[created_at]

    # relationships
    category: Mapped["Category"] = relationship("Category")
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    sizes: Mapped[List["ProductSize"]] = relationship("ProductSize", back_populates="product", cascade="all, delete-orphan")
    colors: Mapped[List["ProductColor"]] = relationship("ProductColor", back_populates="product", cascade="all, delete-orphan")

class ProductImage(Base):
    __tablename__ = "product_images"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(200))
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship("Product", back_populates="images")

class ProductSize(Base):
    __tablename__ = "product_sizes"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    size_label: Mapped[str] = mapped_column(String(20), nullable=False)
    chest_cm: Mapped[Optional[str]] = mapped_column(String(20))
    waist_cm: Mapped[Optional[str]] = mapped_column(String(20))
    hips_cm: Mapped[Optional[str]] = mapped_column(String(20))
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    sku_variant: Mapped[Optional[str]] = mapped_column(String(100))

    product: Mapped["Product"] = relationship("Product", back_populates="sizes")

class ProductColor(Base):
    __tablename__ = "product_colors"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    color_name: Mapped[str] = mapped_column(String(50), nullable=False)
    color_hex: Mapped[Optional[str]] = mapped_column(String(7))

    product: Mapped["Product"] = relationship("Product", back_populates="colors")

class SizeChart(Base):
    __tablename__ = "size_charts"

    category: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(10), nullable=False)  # EU, US, RU
    size_mapping: Mapped[dict] = mapped_column(JSON, nullable=False)  # {"S": {"chest": 90, "waist": 70}}
    