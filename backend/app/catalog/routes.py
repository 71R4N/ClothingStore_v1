from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, Optional, List
from backend.app.catalog.schemas import CategoryCreate, CategoryResponse, ProductCreate, ProductResponse, ProductUpdate
from backend.app.catalog.services import CatalogService
from backend.app.catalog.dependencies import get_catalog_service
from backend.app.auth.dependencies import get_current_user
from backend.app.users.models import User, UserRole

router = APIRouter(prefix="/catalog", tags=["Catalog"])
CatalogServiceDep = Annotated[CatalogService, Depends(get_catalog_service)]

# Categories
@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(service: CatalogServiceDep):
    return await service.get_categories()

@router.post("/categories", response_model=dict)
async def create_category(
    data: CategoryCreate,
    service: CatalogServiceDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    cat_id = await service.create_category(data)
    return {"id": cat_id}

# Products
@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    service: CatalogServiceDep,
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    filters = {}
    if category_id:
        filters["category_id"] = category_id
    if min_price:
        filters["min_price"] = min_price
    if max_price:
        filters["max_price"] = max_price
    if search:
        filters["search"] = search
    return await service.list_products(filters, limit, offset)

@router.get("/products/{slug}", response_model=ProductResponse)
async def get_product(slug: str, service: CatalogServiceDep):
    product = await service.get_product_by_slug(slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=dict)
async def create_product(
    data: ProductCreate,
    service: CatalogServiceDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    prod_id = await service.create_product(data)
    return {"id": prod_id}

@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    service: CatalogServiceDep,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    updated = await service.update_product(product_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated
