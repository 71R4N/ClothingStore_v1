from app.core.repository import SqlAlchemyRepo
from app.notifications.models import Notification
from sqlalchemy import select, update

class NotificationRepo(SqlAlchemyRepo):
    model = Notification

    async def get_user_notifications(self, user_id: str, unread_only: bool = False, skip: int = 0, limit: int = 50):
        stmt = select(self.model).where(self.model.user_id == user_id)
        if unread_only:
            stmt = stmt.where(self.model.is_read == False)
        stmt = stmt.order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def mark_as_read(self, user_id: str, notification_ids: list[str] = None):
        if notification_ids:
            stmt = update(self.model).where(self.model.id.in_(notification_ids), self.model.user_id == user_id).values(is_read=True)
        else:
            stmt = update(self.model).where(self.model.user_id == user_id).values(is_read=True)
        await self.session.execute(stmt)
        await self.session.commit()
        