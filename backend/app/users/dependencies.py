from typing import Annotated

from fastapi import Depends
from app.core.database import SessionDbDep
from app.users.repositories import UserRepo
from app.users.services import UserService

def user_service(session: SessionDbDep) -> UserService:
    return UserService(UserRepo(session))

UserServiceDep = Annotated[UserService, Depends(user_service)]
