from fastapi import APIRouter, Query, Cookie
from app.orders.schemas import OrderCreate, OrderRead, OrderStatusUpdate
from app.orders.dependencies import OrderServiceDep
from app.auth.dependencies import OptionalUserDep, CurrentUserDep
from uuid import UUID
from app.core.exceptions import ForbiddenException

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(
        data: OrderCreate,
        order_svc: OrderServiceDep,
        current_user: OptionalUserDep,
        session_id: str | None = Cookie(None)
):
    user_id = current_user.id if current_user else None

    order = await order_svc.create_order(user_id, session_id, data)
    return order


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
        order_id: UUID,
        order_svc: OrderServiceDep,
        current_user: OptionalUserDep
):
    order = await order_svc.get_order(order_id)

    # Проверка доступа: только владелец или админ
    if current_user:
        if order.user_id and order.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException()
    elif order.user_id:
        # Гость пытается получить заказ авторизованного пользователя
        raise ForbiddenException()

    return order


@router.get("/", response_model=list[OrderRead])
async def list_orders(
        order_svc: OrderServiceDep,
        current_user: CurrentUserDep,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100)
):
    return await order_svc.get_user_orders(current_user.id, skip, limit)


@router.patch("/{order_id}/status", response_model=OrderRead)
async def update_status(
        order_id: UUID,
        data: OrderStatusUpdate,
        order_svc: OrderServiceDep,
        current_user: CurrentUserDep
):
    if current_user.role != "admin":
        raise ForbiddenException()

    return await order_svc.update_status(order_id, data.status)
