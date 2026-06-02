from typing import Annotated
from fastapi import Depends
from app.core.database import SessionDbDep
from app.orders.repositories import OrderRepo, OrderItemRepo
from app.orders.services import OrderService
from app.cart.services import CartService
from app.cart.repositories import CartRepo
from app.catalog.repositories import ProductVariantRepo


def get_order_service(session: SessionDbDep) -> OrderService:
    cart_service = CartService(
        cart_repo=CartRepo(session),
        variant_repo=ProductVariantRepo(session)
    )

    return OrderService(
        order_repo=OrderRepo(session),
        order_item_repo=OrderItemRepo(session),
        cart_service=cart_service,
        variant_repo=ProductVariantRepo(session)
    )


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
