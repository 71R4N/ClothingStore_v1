from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import Annotated, Optional
from backend.app.cart.schemas import CartItemCreate, CartItemUpdate, CartResponse
from backend.app.cart.services import CartService
from backend.app.cart.dependencies import get_cart_service
from backend.app.auth.dependencies import get_current_user_optional, get_current_user
from backend.app.users.models import User
from uuid import UUID

router = APIRouter(prefix="/cart", tags=["Cart"])
CartServiceDep = Annotated[CartService, Depends(get_cart_service)]

def get_session_id(request: Request) -> str:
    session_id = request.cookies.get("session_id")
    if not session_id:
        # middleware должен был создать, но на всякий случай
        raise HTTPException(status_code=400, detail="No session cookie")
    return session_id

@router.get("/", response_model=CartResponse)
async def get_cart(
    request: Request,
    service: CartServiceDep,
    current_user: Optional[User] = Depends(get_current_user_optional)  # реализуем optional dependency
):
    user_id = current_user.id if current_user else None
    session_id = request.cookies.get("session_id") if not user_id else None
    return await service.get_cart(user_id, session_id)

@router.post("/items")
async def add_to_cart(
    request: Request,
    item: CartItemCreate,
    service: CartServiceDep,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    session_id = request.cookies.get("session_id") if not user_id else None
    if not user_id and not session_id:
        raise HTTPException(status_code=400, detail="No session")
    result = await service.add_item(user_id, session_id, item)
    return result

@router.patch("/items/{item_id}")
async def update_cart_item(
    request: Request,
    item_id: UUID,
    update: CartItemUpdate,
    service: CartServiceDep,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    session_id = request.cookies.get("session_id") if not user_id else None
    success = await service.update_quantity(user_id, session_id, str(item_id), update)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "updated"}

@router.delete("/items/{item_id}")
async def remove_cart_item(
    request: Request,
    item_id: UUID,
    service: CartServiceDep,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    session_id = request.cookies.get("session_id") if not user_id else None
    success = await service.remove_item(user_id, session_id, str(item_id))
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "removed"}
