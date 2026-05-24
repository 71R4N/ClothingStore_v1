from backend.app.core.database import SessionDbDep
from backend.app.catalog.repositories import CategoryRepo, ProductRepo
from backend.app.catalog.services import CatalogService

def get_catalog_service(session: SessionDbDep) -> CatalogService:
    return CatalogService(CategoryRepo(session), ProductRepo(session))
