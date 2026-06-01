from app.core.repository import SqlAlchemyRepo
from app.tryon.models import TryOnSession
from sqlalchemy import select

class TryOnRepo(SqlAlchemyRepo):
    model = TryOnSession

    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 20):
        stmt = select(self.model).where(self.model.user_id == user_id).order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()