from app.core.exceptions import NotFoundException, ConflictException, BaseAppException
from fastapi import status


class PaymentNotFoundError(NotFoundException):
    detail = "Payment not found"


class PaymentAlreadyPaidError(ConflictException):
    detail = "Order already has a successful payment"


class InvalidPaymentStatusError(ConflictException):
    detail = "Invalid payment status for this operation"


class YooKassaAPIError(BaseAppException):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "Payment gateway error"

    def __init__(self, detail: str | None = None):
        super().__init__(detail=detail or self.detail)


class YooKassaConfigError(BaseAppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Payment gateway configuration error"
