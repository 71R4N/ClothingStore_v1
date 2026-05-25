from typing import Annotated

from fastapi import Depends
from app.core.database import SessionDbDep
from app.orders.repositories import OrderRepo, OrderItemRepo, PaymentRepo, ReturnRepo, AddressRepo
from app.orders.services import OrderService
from app.cart.services import CartService
from app.cart.repositories import CartRepo
from app.catalog.repositories import ProductRepo

def get_order_service(session: SessionDbDep) -> OrderService:
    cart_service = CartService(CartRepo(session), ProductRepo(session))
    return OrderService(
        order_repo=OrderRepo(session),
        order_item_repo=OrderItemRepo(session),
        payment_repo=PaymentRepo(session),
        return_repo=ReturnRepo(session),
        address_repo=AddressRepo(session),
        cart_service=cart_service
    )

OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
