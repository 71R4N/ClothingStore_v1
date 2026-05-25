from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Category
class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    children: List["CategoryRead"] = []
    model_config = {"from_attributes": True}

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

# ProductImage
class ProductImageBase(BaseModel):
    url: str
    alt_text: Optional[str] = None
    is_main: bool = False
    sort_order: int = 0

class ProductImageRead(ProductImageBase):
    id: int
    model_config = {"from_attributes": True}

# ProductSize
class ProductSizeBase(BaseModel):
    size_label: str
    chest_cm: Optional[str] = None
    waist_cm: Optional[str] = None
    hips_cm: Optional[str] = None
    stock_quantity: int = 0
    sku_variant: str

class ProductSizeRead(ProductSizeBase):
    id: int
    model_config = {"from_attributes": True}

# ProductColor
class ProductColorBase(BaseModel):
    color_name: str
    color_hex: str

class ProductColorRead(ProductColorBase):
    id: int
    model_config = {"from_attributes": True}

# Product
class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    price: float
    old_price: Optional[float] = None
    category_id: int
    brand: Optional[str] = None
    sku: str
    is_active: bool = True

class ProductCreate(ProductBase):
    images: Optional[List[ProductImageBase]] = []
    sizes: Optional[List[ProductSizeBase]] = []
    colors: Optional[List[ProductColorBase]] = []

class ProductRead(ProductBase):
    id: int
    created_at: datetime
    images: List[ProductImageRead] = []
    sizes: List[ProductSizeRead] = []
    colors: List[ProductColorRead] = []
    model_config = {"from_attributes": True}

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    old_price: Optional[float] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = None

# SizeChart
class SizeChartBase(BaseModel):
    category: str
    region: str
    size_mapping: dict

class SizeChartRead(SizeChartBase):
    id: int
    model_config = {"from_attributes": True}
    