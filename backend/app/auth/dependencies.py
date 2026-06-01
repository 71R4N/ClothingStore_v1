from fastapi import Depends, Request
from typing import Annotated
from app.core.database import SessionDbDep
from app.core.security import decode_access_token
from app.users.repositories import UserRepo
from app.users.services import UserService
from app.users.models import User
from app.auth.exceptions import InvalidCredentialsError

def user_service(session: SessionDbDep) -> UserService:
    return UserService(UserRepo(session))

UserServiceDep = Annotated[UserService, Depends(user_service)]


async def get_current_user(
        request: Request,
        user_service: UserServiceDep = None,
) -> User | None:
    authorization = request.headers.get("Authorization")
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        return None

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    user_id = payload["sub"]
    user = await user_service.get_by_id(user_id)
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]
