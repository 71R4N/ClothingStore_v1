from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from typing import Annotated
from uuid import UUID
from app.core.database import SessionDbDep
from app.core.security import decode_access_token
from app.users.repositories import UserRepo
from app.users.services import UserService
from app.users.models import User


def get_user_service(session: SessionDbDep) -> UserService:
    return UserService(UserRepo(session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
        request: Request,
        user_service: UserService = Depends(get_user_service),
) -> User:
    authorization = request.headers.get("Authorization")
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        user_id = UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    try:
        user = await user_service.get_by_id(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return user


# Обязательная авторизация (для защищенных роутов)
CurrentUserDep = Annotated[User, Depends(get_current_user)]


# Опциональная авторизация (для роутов, где пользователь может быть гостем)
async def get_optional_user(
        request: Request,
        user_service: UserService = Depends(get_user_service),
) -> User | None:
    try:
        return await get_current_user(request, user_service)
    except HTTPException:
        return None


OptionalUserDep = Annotated[User | None, Depends(get_optional_user)]
