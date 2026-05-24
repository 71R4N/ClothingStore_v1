from backend.app.core.repository import AbstractRepo
from backend.app.users.schemas import RegisterUserSchema, ResponseUserSchema, UpdateUserSchema
from backend.app.core.security import hash_password, verify_password
from backend.app.users.models import User
from typing import Optional

class UserService:
    def __init__(self, user_repo: AbstractRepo):
        self.user_repo = user_repo


    async def create_user(self, data: RegisterUserSchema) -> int:
        user_dict = data.model_dump()
        user_dict["password_hash"] = hash_password(user_dict.pop("password"))
        return await self.user_repo.create(user_dict)

    async def get_user_by_id(self, user_id: int) -> Optional[ResponseUserSchema]:
        user = await self.user_repo.get_by_id(user_id)
        if user:
            return ResponseUserSchema.model_validate(user)
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        # прямой вызов метода репозитория (расширенного)
        if hasattr(self.user_repo, "get_by_email"):
            return await self.user_repo.get_by_email(email)
        return None

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def update_user(self, user_id: int, data: UpdateUserSchema) -> Optional[ResponseUserSchema]:
        if data.password:
            data.password = hash_password(data.password)
        updated = await self.user_repo.update(user_id, data)
        if updated:
            return ResponseUserSchema.model_validate(updated)
        return None

    async def delete_user(self, user_id: int) -> bool:
        deleted_id = await self.user_repo.delete(user_id)
        return deleted_id > 0