from app.notifications.repositories import NotificationRepo
from app.notifications.schemas import NotificationRead

class NotificationService:
    def __init__(self, repo: NotificationRepo):
        self.repo = repo

    async def send(self, user_id: str, type: str, title: str, message: str):
        # создание уведомления (может вызываться из Celery задач)
        notif = Notification(user_id=user_id, type=type, title=title, message=message)
        # используем репозиторий
        return await self.repo.create(notif)

    async def get_user_notifications(self, user_id: str, unread_only: bool = False, skip: int = 0, limit: int = 50):
        return await self.repo.get_user_notifications(user_id, unread_only, skip, limit)

    async def mark_read(self, user_id: str, notification_ids: list[str] = None):
        await self.repo.mark_as_read(user_id, notification_ids)
