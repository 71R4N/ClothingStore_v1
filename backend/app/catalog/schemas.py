from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    tryon_category: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    children: List["CategoryRead"] = Field(default_factory=list)
    model_config = {"from_attributes": True}


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductSizeBase(BaseModel):
    size_label: str
    chest_cm: Optional[str] = None
    waist_cm: Optional[str] = None
    hips_cm: Optional[str] = None
    label_size: Optional[str] = None
    height_cm: Optional[str] = None


class ProductSizeRead(ProductSizeBase):
    id: int
    model_config = {"from_attributes": True}


class ProductColorBase(BaseModel):
    color_name: str
    color_hex: str


class ProductColorRead(ProductColorBase):
    id: int
    model_config = {"from_attributes": True}


class ProductVariantBase(BaseModel):
    color_id: int
    size_id: int
    sku: str
    stock_quantity: int = 0
    price: float
    image_url: Optional[str] = None
    attributes: Optional[dict] = None


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantRead(ProductVariantBase):
    id: int
    product_id: int
    color: Optional[ProductColorRead] = None
    size: Optional[ProductSizeRead] = None
    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    category_id: int
    brand: Optional[str] = None
    brand_logo: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    sizes: List[ProductSizeBase] = Field(default_factory=list)
    colors: List[ProductColorBase] = Field(default_factory=list)
    variants: List[ProductVariantCreate] = Field(default_factory=list)


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    category: Optional[CategoryRead] = None
    sizes: List[ProductSizeRead] = Field(default_factory=list)
    colors: List[ProductColorRead] = Field(default_factory=list)
    variants: List[ProductVariantRead] = Field(default_factory=list)
    model_config = {"from_attributes": True}


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    brand_logo: Optional[str] = None
    is_active: Optional[bool] = None
