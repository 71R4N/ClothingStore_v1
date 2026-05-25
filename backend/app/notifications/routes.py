from fastapi import APIRouter, Depends, Query
from app.notifications.schemas import NotificationRead
from app.notifications.dependencies import NotificationServiceDep
from app.notifications.services import NotificationService
from app.auth.dependencies import CurrentUserDep
from typing import Annotated

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=list[NotificationRead])
async def get_notifications(
    current_user: CurrentUserDep,
    notif_svc: NotificationServiceDep,
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50
):
    return await notif_svc.get_user_notifications(str(current_user.id), unread_only, skip, limit)

@router.post("/mark-read", status_code=204)
async def mark_read(
    current_user: CurrentUserDep,
    notif_svc: NotificationServiceDep,
    notification_ids: list[str] | None = None
):
    await notif_svc.mark_read(str(current_user.id), notification_ids)
    