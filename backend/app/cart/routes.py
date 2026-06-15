from fastapi import APIRouter, Response, Cookie, Depends
from app.cart.schemas import CartItemCreate, CartItemUpdate, CartItemRead, CartResponse
from app.cart.dependencies import CartServiceDep
from app.auth.dependencies import OptionalUserDep
from uuid import UUID, uuid4

router = APIRouter(prefix="/cart", tags=["cart"])


async def get_user_or_session(
        current_user: OptionalUserDep,
        session_id: str | None = Cookie(None)
) -> tuple[UUID | None, str | None, bool]:
    user_id = current_user.id if current_user else None
    is_new = False

    if not user_id and not session_id:
        session_id = str(uuid4())
        is_new = True

    return user_id, session_id, is_new


@router.get("/", response_model=CartResponse)
async def get_cart(
        cart_svc: CartServiceDep,
        response: Response,
        user_session: tuple = Depends(get_user_or_session)
):
    user_id, session_id, is_new = user_session

    if is_new and session_id:
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 30
        )

    items = await cart_svc.get_cart(user_id, session_id)
    total = sum((item.variant.price if item.variant else 0) * item.quantity for item in items)
    return CartResponse(items=items, total=float(total))


@router.post("/items", response_model=CartItemRead, status_code=201)
async def add_item(
        data: CartItemCreate,
        cart_svc: CartServiceDep,
        response: Response,
        user_session: tuple = Depends(get_user_or_session)
):
    user_id, session_id, is_new = user_session

    if is_new and session_id:
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 30
        )

    return await cart_svc.add_to_cart(user_id, session_id, data)


@router.patch("/items/{item_id}", response_model=CartItemRead)
async def update_item(
        item_id: UUID,
        data: CartItemUpdate,
        cart_svc: CartServiceDep,
):
    return await cart_svc.update_item(item_id, data.quantity)


@router.delete("/items/{item_id}", status_code=204)
async def remove_item(
        item_id: UUID,
        cart_svc: CartServiceDep,
):
    await cart_svc.remove_item(item_id)


@router.delete("/", status_code=204)
async def clear_cart(
        cart_svc: CartServiceDep,
        user_session: tuple = Depends(get_user_or_session)
):
    user_id, session_id, _ = user_session
    await cart_svc.clear_cart(user_id, session_id)
