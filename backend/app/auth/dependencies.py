from fastapi import Depends, Header
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
    authorization: Annotated[str | None, Header()] = None,
    user_service: UserServiceDep = None,
) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    user_id = payload["sub"]
    user = await user_service.get_by_id(user_id)
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]
