from app.core.repository import AbstractRepo
from app.users.schemas import UserCreate, UserRead, UserUpdate
from app.users.exceptions import UserNotFoundError

class UserService:
    def __init__(self, user_repo: AbstractRepo):
        self.user_repo = user_repo

    async def create_user(self, data: UserCreate):
        user_id = await self.user_repo.create(data)
        return user_id

    async def get_by_id(self, id):
        user = await self.user_repo.read_by_id(id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_by_email(self, email: str):
        user = await self.user_repo.get_by_email(email)
        return user  # может быть None

    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.user_repo.read_all(skip, limit)

    async def update(self, id, data: UserUpdate, partial: bool = True):
        await self.get_by_id(id)  # проверка существования
        updated = await self.user_repo.update(data, id, exclude_unset=partial)
        return updated

    async def delete(self, id):
        await self.get_by_id(id)
        deleted_id = await self.user_repo.delete(id)
        return deleted_id
