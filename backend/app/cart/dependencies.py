from typing import Annotated
from fastapi import Depends
from app.core.database import SessionDbDep
from app.cart.repositories import CartRepo
from app.cart.services import CartService
from app.catalog.repositories import ProductVariantRepo


def get_cart_service(session: SessionDbDep) -> CartService:
    return CartService(
        cart_repo=CartRepo(session),
        variant_repo=ProductVariantRepo(session)
    )


CartServiceDep = Annotated[CartService, Depends(get_cart_service)]