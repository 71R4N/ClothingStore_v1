from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from decimal import Decimal

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class ProductImageBase(BaseModel):
    url: str
    alt_text: Optional[str] = None
    is_main: bool = False
    sort_order: int = 0

class ProductImageResponse(ProductImageBase):
    id: int

class ProductSizeBase(BaseModel):
    size_label: str
    chest_cm: Optional[str] = None
    waist_cm: Optional[str] = None
    hips_cm: Optional[str] = None
    stock_quantity: int = 0
    sku_variant: Optional[str] = None

class ProductSizeResponse(ProductSizeBase):
    id: int

class ProductColorBase(BaseModel):
    color_name: str
    color_hex: Optional[str] = None

class ProductColorResponse(ProductColorBase):
    id: int

class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    price: Decimal
    old_price: Optional[Decimal] = None
    category_id: int
    brand: Optional[str] = None
    sku: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    images: Optional[List[ProductImageBase]] = []
    sizes: Optional[List[ProductSizeBase]] = []
    colors: Optional[List[ProductColorBase]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    old_price: Optional[Decimal] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: str
    images: List[ProductImageResponse] = []
    sizes: List[ProductSizeResponse] = []
    colors: List[ProductColorResponse] = []
    class Config:
        from_attributes = True
        