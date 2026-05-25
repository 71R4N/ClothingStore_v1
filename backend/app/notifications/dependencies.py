from typing import Annotated

from fastapi import Depends
from app.core.database import SessionDbDep
from app.notifications.repositories import NotificationRepo
from app.notifications.services import NotificationService

def get_notification_service(session: SessionDbDep) -> NotificationService:
    return NotificationService(NotificationRepo(session))

NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
