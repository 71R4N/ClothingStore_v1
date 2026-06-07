from typing import Annotated
from fastapi import Depends
from app.core.database import SessionDbDep
from app.returns.repositories import ReturnRepo
from app.returns.services import ReturnService
from app.orders.repositories import OrderRepo, OrderItemRepo
from app.catalog.repositories import ProductVariantRepo


def get_return_service(session: SessionDbDep) -> ReturnService:
    """Фабрика для создания ReturnService."""
    return ReturnService(
        return_repo=ReturnRepo(session),
        order_repo=OrderRepo(session),
        order_item_repo=OrderItemRepo(session),
        variant_repo=ProductVariantRepo(session),
    )

ReturnServiceDep = Annotated[ReturnService, Depends(get_return_service)]