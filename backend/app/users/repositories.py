from backend.app.core.repository import SQLAlchemyRepo
from backend.app.users.models import User
from backend.app.users.schemas import RegisterUserSchema, UpdateUserSchema

class UserRepo(SQLAlchemyRepo[User, RegisterUserSchema]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        from sqlalchemy import select
        stmt = select(self.model).where(self.model.email == email)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()