from app.core.exceptions import (
    NotFoundException, ConflictException, ForbiddenException,
    BaseAppException
)
from fastapi import status


class ReturnNotFoundError(NotFoundException):
    """Заявка на возврат не найдена."""
    detail = "Return request not found"


class ReturnItemNotFoundError(NotFoundException):
    """Позиция возврата не найдена."""
    detail = "Return item not found"


class OrderNotDeliveredError(ConflictException):
    """Возврат возможен только для доставленных заказов."""
    detail = "Returns are only available for delivered orders"


class ReturnPeriodExceededError(ConflictException):
    """Превышен срок возврата (14 дней)."""
    detail = "Return period (14 days) has been exceeded"


class ReturnAlreadyExistsError(ConflictException):
    """Для указанных товаров уже существует активная заявка."""
    detail = "Active return request already exists for these items"


class InvalidReturnQuantityError(ConflictException):
    """Недопустимое количество для возврата."""
    detail = "Invalid return quantity"


class InvalidReturnStatusTransitionError(ConflictException):
    """Недопустимый переход между статусами возврата."""
    detail = "Invalid return status transition"


class ReturnLimitExceededError(BaseAppException):
    """Превышен лимит возвратов для пользователя."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Return limit exceeded for this period"
