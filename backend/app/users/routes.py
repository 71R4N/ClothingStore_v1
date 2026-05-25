from fastapi import APIRouter, Depends, status
from app.users.schemas import UserRead, UserUpdate, UserCreate
from app.users.dependencies import user_service as get_user_service
from app.users.services import UserService
from app.auth.dependencies import CurrentUserDep
from typing import Annotated
from uuid import UUID

router = APIRouter(prefix="/users", tags=["users"])
UserSvcDep = Annotated[UserService, Depends(get_user_service)]

@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUserDep):
    return current_user

@router.patch("/me", response_model=UserRead)
async def update_me(
    update_data: UserUpdate,
    current_user: CurrentUserDep,
    user_svc: CurrentUserDep,
):
    updated = await user_svc.update(str(current_user.id), update_data, partial=True)
    return updated

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, user_svc: UserSvcDep):
    return await user_svc.get_by_id(str(user_id))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, user_svc: UserSvcDep, current_user: CurrentUserDep):
    # только админ или сам пользователь может удалить
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException()
    await user_svc.delete(str(user_id))
