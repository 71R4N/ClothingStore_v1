from fastapi import APIRouter, Depends, Query, Path
from app.catalog.schemas import (CategoryCreate, CategoryRead, CategoryUpdate,
                                 ProductCreate, ProductRead, ProductUpdate)
from app.catalog.dependencies import CatalogServiceDep
from typing import Optional

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.post("/categories", response_model=CategoryRead, status_code=201)
async def create_category(data: CategoryCreate, service: CatalogServiceDep):
    cat_id = await service.create_category(data)
    return await service.get_category(cat_id)

@router.get("/categories/tree", response_model=list[CategoryRead])
async def category_tree(service: CatalogServiceDep):
    return await service.get_category_tree()

@router.get("/categories/{slug}", response_model=CategoryRead)
async def get_category(slug: str, service: CatalogServiceDep):
    return await service.get_category_by_slug(slug)

@router.patch("/categories/{category_id}", response_model=CategoryRead)
async def update_category(category_id: int, data: CategoryUpdate, service: CatalogServiceDep):
    return await service.update_category(category_id, data)

@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: int, service: CatalogServiceDep):
    await service.delete_category(category_id)

@router.post("/products", response_model=ProductRead, status_code=201)
async def create_product(data: ProductCreate, service: CatalogServiceDep):
    prod_id = await service.create_product(data)
    return await service.get_product(prod_id)

@router.get("/products", response_model=list[ProductRead])
async def list_products(
    service: CatalogServiceDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, pattern="^(price|created_at)$"),
    order: str = Query("asc", pattern="^(asc|desc)$")
):
    return await service.get_products(skip, limit, category_id, search, min_price, max_price, sort_by, order)

@router.get("/products/{slug}", response_model=ProductRead)
async def get_product(slug: str, service: CatalogServiceDep):
    return await service.get_product_by_slug(slug)

@router.patch("/products/{product_id}", response_model=ProductRead)
async def update_product(product_id: int, data: ProductUpdate, service: CatalogServiceDep):
    return await service.update_product(product_id, data)

@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, service: CatalogServiceDep):
    await service.delete_product(product_id)
