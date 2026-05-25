from app.core.repository import SqlAlchemyRepo
from app.users.models import User
from sqlalchemy import select

class UserRepo(SqlAlchemyRepo):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
