from typing import Annotated
from fastapi import Depends
from app.core.database import SessionDbDep
from app.catalog.repositories import CategoryRepo, ProductRepo, ProductVariantRepo
from app.catalog.services import CatalogService


def get_catalog_service(session: SessionDbDep) -> CatalogService:
    return CatalogService(
        category_repo=CategoryRepo(session),
        product_repo=ProductRepo(session),
        variant_repo=ProductVariantRepo(session),
    )


CatalogServiceDep = Annotated[CatalogService, Depends(get_catalog_service)]