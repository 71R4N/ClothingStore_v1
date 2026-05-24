from typing import Optional
from fastapi import Depends, Request
from backend.app.core.database import SessionDbDep
from backend.app.cart.repositories import CartItemRepo
from backend.app.cart.services import CartService
from backend.app.users.dependencies import get_current_user_optional
from backend.app.users.models import User

def get_cart_repo(session: SessionDbDep) -> CartItemRepo:
    return CartItemRepo(session)

def get_cart_service(
    repo: CartItemRepo = Depends(get_cart_repo)
) -> CartService:
    return CartService(repo)

def get_session_id(request: Request) -> Optional[str]:
    return request.cookies.get("session_id")

def get_cart_service_with_session(
    request: Request,
    service: CartService = Depends(get_cart_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> CartService:
    """
    Dependency, которая добавляет в сервис корзины информацию о пользователе/сессии.
    Можно использовать в эндпоинтах, где нужен контекст.
    """
    user_id = current_user.id if current_user else None
    session_id = request.cookies.get("session_id")
    service.set_context(user_id, session_id)
    return service
