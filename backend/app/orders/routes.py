from fastapi import APIRouter, Depends, Query, Request
from app.orders.schemas import OrderCreate, OrderRead, OrderStatusUpdate, ReturnRequest, ReturnRead, PaymentTransactionRead
from app.orders.dependencies import OrderServiceDep
from app.orders.services import OrderService
from app.auth.dependencies import get_current_user, CurrentUserDep
from typing import Annotated, Optional
from uuid import UUID

from fastapi.openapi.models import Response

from app.core.exceptions import ForbiddenException

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(
    data: OrderCreate,
    order_svc: OrderServiceDep,
    current_user: CurrentUserDep,
    request: Request,
):
    user_id = str(current_user.id) if current_user else None
    session_id = None
    if not user_id:
        session_id = request.cookies.get("cart_session_id")
    order = await order_svc.create_order(user_id, session_id, data)
    return order

@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: UUID, order_svc: OrderServiceDep):
    return await order_svc.get_order(str(order_id))

@router.get("/", response_model=list[OrderRead])
async def list_orders(
    order_svc: OrderServiceDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 20
):
    if not current_user:
        raise ForbiddenException()
    return await order_svc.get_user_orders(str(current_user.id), skip, limit)

@router.patch("/{order_id}/status", response_model=OrderRead)
async def update_status(order_id: UUID, data: OrderStatusUpdate, order_svc: OrderServiceDep):
    await order_svc.update_status(str(order_id), data.status)
    return await order_svc.get_order(str(order_id))

@router.post("/{order_id}/pay", response_model=PaymentTransactionRead)
async def pay_order(order_id: UUID, order_svc: OrderServiceDep):
    return await order_svc.initiate_payment(str(order_id))

@router.post("/{order_id}/return", response_model=ReturnRead, status_code=201)
async def request_return(
    order_id: UUID,
    data: ReturnRequest,
    order_svc: OrderServiceDep,
    current_user: CurrentUserDep
):
    return await order_svc.request_return(str(order_id), str(current_user.id), data)

@router.patch("/returns/{return_id}", response_model=ReturnRead)
async def resolve_return(return_id: UUID, order_svc: OrderServiceDep, status: str = "approved"):
    # Админский доступ нужен, но для простоты опустим
    return await order_svc.process_return(str(return_id), status)
