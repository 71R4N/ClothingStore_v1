from passlib.context import CryptContext
from app.core.repository import AbstractRepo
from app.users.schemas import UserCreate, UserRead, UserUpdate
from app.users.exceptions import UserNotFoundError
from uuid import UUID

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, user_repo: AbstractRepo):
        self.user_repo = user_repo

    async def create_user(self, data: UserCreate) -> UUID:
        hashed_password = pwd_context.hash(data.password)

        user_data = data.model_dump(exclude={"password"})
        user_data["password_hash"] = hashed_password
        user_id = await self.user_repo.create_with_hash(user_data)
        return user_id

    async def get_by_id(self, id: UUID) -> UserRead:
        user = await self.user_repo.read_by_id(id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_by_email(self, email: str):
        return await self.user_repo.get_by_email(email)

    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.user_repo.read_all(skip, limit)

    async def update(self, id: UUID, data: UserUpdate, partial: bool = True):
        await self.get_by_id(id)
        return await self.user_repo.update(data, id, exclude_unset=partial)

    async def delete(self, id: UUID):
        await self.get_by_id(id)
        await self.user_repo.delete(id)
