from fastapi import APIRouter, HTTPException, Query, status
from uuid import UUID

from app.returns.schemas import (
    ReturnCreate, ReturnRead, ReturnActionRequest, ReturnListResponse,
)
from app.returns.dependencies import ReturnServiceDep
from app.returns.exceptions import (
    ReturnNotFoundError,
    OrderNotDeliveredError,
    ReturnPeriodExceededError,
    ReturnAlreadyExistsError,
    InvalidReturnQuantityError,
    InvalidReturnStatusTransitionError,
    ReturnLimitExceededError,
)
from app.auth.dependencies import CurrentUserDep, OptionalUserDep
from app.core.exceptions import ForbiddenException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/returns", tags=["returns"])


# ==================== Пользовательские endpoints ====================

@router.post(
    "/",
    response_model=ReturnRead,
    status_code=status.HTTP_201_CREATED
)
async def create_return(
    data: ReturnCreate,
    return_svc: ReturnServiceDep,
    current_user: OptionalUserDep,
):
    """
    Создаёт заявку на возврат товаров из доставленного заказа.
    Поддерживает как авторизованных пользователей, так и гостей (с email).
    """
    user_id = current_user.id if current_user else None
    guest_email = None if current_user else data.__dict__.get("guest_email")

    try:
        return_obj = await return_svc.create_return_request(
            user_id=user_id,
            guest_email=guest_email,
            data=data,
        )
        return await return_svc.get_return(return_obj.id)

    except (OrderNotDeliveredError, ReturnPeriodExceededError,
            ReturnAlreadyExistsError, InvalidReturnQuantityError,
            ReturnLimitExceededError) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=e.detail
        )


@router.get("/", response_model=ReturnListResponse)
async def list_user_returns(
    return_svc: ReturnServiceDep,
    current_user: CurrentUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """Возвращает список возвратов текущего пользователя."""
    items, total = await return_svc.get_user_returns(
        current_user.id, skip, limit
    )
    return ReturnListResponse(items=items, total=total)


@router.get("/{return_id}", response_model=ReturnRead)
async def get_return(
    return_id: UUID,
    return_svc: ReturnServiceDep,
    current_user: CurrentUserDep,
):
    """Получает детальную информацию о возврате."""
    return_obj = await return_svc.get_return(return_id)

    # Проверка доступа
    if (
        return_obj.user_id
        and return_obj.user_id != current_user.id
        and current_user.role != "admin"
    ):
        raise ForbiddenException(detail="Access denied to this return")

    return return_obj


@router.post("/{return_id}/cancel", response_model=ReturnRead)
async def cancel_return(
    return_id: UUID,
    return_svc: ReturnServiceDep,
    current_user: CurrentUserDep,
):
    """Отменяет заявку на возврат (только для статуса PENDING)."""
    try:
        return_obj = await return_svc.cancel_return(return_id, current_user.id)
        return await return_svc.get_return(return_obj.id)
    except InvalidReturnStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=e.detail
        )


# ==================== Административные endpoints ====================

@router.get("/admin/pending", response_model=list[ReturnRead])
async def list_pending_returns(
    return_svc: ReturnServiceDep,
    current_user: CurrentUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Возвращает список заявок, ожидающих рассмотрения (только admin)."""
    if current_user.role != "admin":
        raise ForbiddenException()
    return await return_svc.get_pending_returns(skip, limit)


@router.post("/{return_id}/action", response_model=ReturnRead)
async def process_return_action(
    return_id: UUID,
    data: ReturnActionRequest,
    return_svc: ReturnServiceDep,
    current_user: CurrentUserDep,
):
    """
    Обрабатывает административное действие: approve или reject.
    При одобрении автоматически запускается возврат средств.
    """
    if current_user.role != "admin":
        raise ForbiddenException()

    try:
        if data.action == "approve":
            return_obj = await return_svc.approve_return(
                return_id, current_user.id
            )
        elif data.action == "reject":
            if not data.rejection_reason:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rejection reason is required"
                )
            return_obj = await return_svc.reject_return(
                return_id, current_user.id, data.rejection_reason
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown action: {data.action}"
            )

        return await return_svc.get_return(return_obj.id)

    except InvalidReturnStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail
        )
