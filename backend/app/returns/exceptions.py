from app.core.exceptions import (
    NotFoundException, ConflictException, ForbiddenException,
    BaseAppException
)
from fastapi import status


class ReturnNotFoundError(NotFoundException):
    detail = "Return request not found"


class ReturnItemNotFoundError(NotFoundException):
    detail = "Return item not found"


class OrderNotDeliveredError(ConflictException):
    detail = "Returns are only available for delivered orders"


class ReturnPeriodExceededError(ConflictException):
    detail = "Return period (14 days) has been exceeded"


class ReturnAlreadyExistsError(ConflictException):
    detail = "Active return request already exists for these items"


class InvalidReturnQuantityError(ConflictException):
    detail = "Invalid return quantity"


class InvalidReturnStatusTransitionError(ConflictException):
    detail = "Invalid return status transition"


class ReturnLimitExceededError(BaseAppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Return limit exceeded for this period"
