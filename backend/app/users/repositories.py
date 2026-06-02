from app.core.repository import SqlAlchemyRepo
from app.users.models import User
from sqlalchemy import select, insert

class UserRepo(SqlAlchemyRepo):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_with_hash(self, user_data: dict) -> UUID:
        stmt = insert(self.model).values(**user_data).returning(self.model.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()
