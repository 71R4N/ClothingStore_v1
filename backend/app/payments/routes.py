from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from app.payments.schemas import (
    PaymentCreate,
    PaymentRead,
    PaymentInitiateResponse,
    PaymentPollResponse,
)
from app.payments.dependencies import PaymentServiceDep
from app.payments.exceptions import (
    PaymentNotFoundError,
    PaymentAlreadyPaidError,
    InvalidPaymentStatusError,
    YooKassaAPIError,
)
from app.auth.dependencies import CurrentUserDep
from app.core.exceptions import ForbiddenException, NotFoundException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/initiate",
    response_model=PaymentInitiateResponse,
    status_code=status.HTTP_201_CREATED
)
async def initiate_payment(
    data: PaymentCreate,
    current_user: CurrentUserDep,
    payment_svc: PaymentServiceDep,
):
    try:
        payment = await payment_svc.create_payment_for_order(data.order_id)

        if not payment.confirmation_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get confirmation URL from YooKassa"
            )

        return PaymentInitiateResponse(
            payment_id=payment.id,
            yookassa_payment_id=payment.yookassa_payment_id,
            confirmation_url=payment.confirmation_url,
            status=payment.status.value,
            is_test=payment.is_test,
        )
    except PaymentAlreadyPaidError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order already has a successful payment"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except YooKassaAPIError as e:
        logger.error(f"Payment initiation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment service unavailable"
        )


@router.get(
    "/order/{order_id}/status",
    response_model=PaymentPollResponse
)
async def poll_order_payment_status(
    order_id: UUID,
    current_user: CurrentUserDep,
    payment_svc: PaymentServiceDep,
):
    try:
        payment = await payment_svc.poll_payment_status(order_id)

        order = await payment_svc.order_repo.read_by_id(order_id)
        if order and order.user_id:
            if (
                order.user_id != current_user.id
                and current_user.role != "admin"
            ):
                raise ForbiddenException()

        return PaymentPollResponse(
            id=payment.id,
            order_id=payment.order_id,
            status=payment.status.value,
            payment_method=(
                payment.payment_method.value
                if payment.payment_method
                else None
            ),
            amount=float(payment.amount),
            is_test=payment.is_test,
            updated_at=payment.updated_at,
        )
    except PaymentNotFoundError:
        raise NotFoundException(detail="Payment not found")
    except YooKassaAPIError:
        payment = await payment_svc.payment_repo.get_by_order_id(order_id)
        if payment:
            return PaymentPollResponse(
                id=payment.id,
                order_id=payment.order_id,
                status=payment.status.value,
                payment_method=(
                    payment.payment_method.value
                    if payment.payment_method
                    else None
                ),
                amount=float(payment.amount),
                is_test=payment.is_test,
                updated_at=payment.updated_at,
            )
        raise NotFoundException(detail="Payment not found")


@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: UUID,
    current_user: CurrentUserDep,
    payment_svc: PaymentServiceDep,
):
    payment = await payment_svc.payment_repo.read_by_id(payment_id)
    if not payment:
        raise NotFoundException(detail="Payment not found")

    order = await payment_svc.order_repo.read_by_id(payment.order_id)
    if order and order.user_id:
        if (
            order.user_id != current_user.id
            and current_user.role != "admin"
        ):
            raise ForbiddenException()

    return payment


@router.get("/order/{order_id}", response_model=list[PaymentRead])
async def get_order_payments(
    order_id: UUID,
    current_user: CurrentUserDep,
    payment_svc: PaymentServiceDep,
):
    order = await payment_svc.order_repo.read_by_id(order_id)
    if not order:
        raise NotFoundException(detail="Order not found")

    if (
        order.user_id
        and order.user_id != current_user.id
        and current_user.role != "admin"
    ):
        raise ForbiddenException()

    return await payment_svc.get_order_payments(order_id)


@router.post("/{payment_id}/cancel", response_model=PaymentRead)
async def cancel_payment(
    payment_id: UUID,
    current_user: CurrentUserDep,
    payment_svc: PaymentServiceDep,
):
    try:
        payment = await payment_svc.cancel_payment(payment_id)
        return payment
    except PaymentNotFoundError:
        raise NotFoundException(detail="Payment not found")
    except InvalidPaymentStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except YooKassaAPIError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to cancel payment"
        )
