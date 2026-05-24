from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from backend.app.users.schemas import RegisterUserSchema, UpdateUserSchema, ResponseUserSchema
from backend.app.users.services import UserService
from backend.app.users.dependencies import get_user_service
from backend.app.auth.dependencies import get_current_user  # будет создано позже
from backend.app.users.models import User

router = APIRouter(prefix="/users", tags=["Users"])
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

@router.post("/register", response_model=dict)
async def register_user(user_data: RegisterUserSchema, service: UserServiceDep):
    # проверка на существующего пользователя
    existing = await service.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = await service.create_user(user_data)
    return {"user_id": user_id, "message": "User created successfully"}

@router.get("/me", response_model=ResponseUserSchema)
async def get_current_user_info(current_user: Annotated[User, Depends(get_current_user)]):
    return ResponseUserSchema.model_validate(current_user)

@router.patch("/me", response_model=ResponseUserSchema)
async def update_current_user(
    user_data: UpdateUserSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: UserServiceDep
):
    updated = await service.update_user(current_user.id, user_data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/me", response_model=dict)
async def delete_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
    service: UserServiceDep
):
    success = await service.delete_user(current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
