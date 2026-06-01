from fastapi import APIRouter, Depends, Header, Cookie, Request, Response
from app.cart.schemas import CartItemCreate, CartItemUpdate, CartItemRead, CartResponse
from app.cart.dependencies import CartServiceDep
from app.cart.services import CartService
from app.auth.dependencies import get_current_user  # или CurrentUserDep
from typing import Annotated, Optional
from uuid import UUID, uuid4

router = APIRouter(prefix="/cart", tags=["cart"])
CartServ = Annotated[CartService, Depends(CartServiceDep)]

# Идентификация пользователя/сессии
async def get_user_or_session(
    request: Request,
    response: Response,   # добавили response
    current_user = Depends(get_current_user)
) -> tuple[Optional[str], Optional[str], bool]:
    user_id = str(current_user.id) if current_user else None
    session_id = None
    is_new = False
    if not user_id:
        session_id = request.cookies.get("cart_session_id")
        if not session_id:
            session_id = str(uuid4())
            is_new = True
    return user_id, session_id, is_new

@router.get("/", response_model=CartResponse)
async def get_cart(
    cart_svc: CartServ,
    response: Response,
    user_session: tuple = Depends(get_user_or_session)
):
    user_id, session_id, is_new = user_session
    if is_new:
        response.set_cookie(key="cart_session_id", value=session_id, httponly=True, max_age=60*60*24*30)
    items = await cart_svc.get_cart(user_id, session_id)
    total = sum((item.product.price if item.product else 0) * item.quantity for item in items)
    return {"items": items, "total": total}

@router.post("/items", response_model=CartItemRead, status_code=201)
async def add_item(
    data: CartItemCreate,
    cart_svc: CartServ,
    response: Response,
    user_session: tuple = Depends(get_user_or_session)
):
    user_id, session_id, is_new = user_session
    if is_new:
        response.set_cookie(key="cart_session_id", value=session_id, httponly=True, max_age=60 * 60 * 24 * 30)
    return await cart_svc.add_to_cart(user_id, session_id, data)

@router.patch("/items/{item_id}", response_model=CartItemRead)
async def update_item(
    item_id: UUID,
    data: CartItemUpdate,
    cart_svc: CartServ,
    user_session: tuple = Depends(get_user_or_session)
):
    return await cart_svc.update_item(str(item_id), data.quantity)

@router.delete("/items/{item_id}", status_code=204)
async def remove_item(
    item_id: UUID,
    cart_svc: CartServ,
    user_session: tuple = Depends(get_user_or_session)
):
    await cart_svc.remove_item(str(item_id))
    return Response(status_code=204)
