import logging
from typing import Optional
from uuid import UUID
from app.payments.repositories import PaymentRepo
from app.payments.models import Payment, PaymentStatus, PaymentMethod
from app.payments.client import yookassa_client, YooKassaAPIError
from app.payments.exceptions import (
    PaymentNotFoundError,
    PaymentAlreadyPaidError,
    InvalidPaymentStatusError,
)
from app.orders.repositories import OrderRepo
from app.orders.models import Order, OrderStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class PaymentService:
    """Сервис для работы с платежами."""

    def __init__(self, payment_repo: PaymentRepo, order_repo: OrderRepo):
        self.payment_repo = payment_repo
        self.order_repo = order_repo

    async def create_payment_for_order(self, order_id: UUID) -> Payment:
        """
        Создает платеж в ЮKassa для указанного заказа.
        Возвращает созданный объект Payment.
        """
        order = await self.order_repo.read_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.status != OrderStatus.PENDING:
            raise ValueError(
                f"Order is not in PENDING status: {order.status}"
            )

        existing_payment = await self.payment_repo.get_by_order_id(order_id)
        if (
                existing_payment
                and existing_payment.status == PaymentStatus.SUCCEEDED
        ):
            raise PaymentAlreadyPaidError()

        description = f"Заказ #{str(order.id)[:8]} на сумму {order.total} руб."

        # Формируем URL возврата с order_id
        return_url = f"{settings.YOOKASSA_RETURN_URL}?order_id={order.id}"
        cancel_url = f"{settings.YOOKASSA_CANCEL_URL}?order_id={order.id}"

        try:
            yookassa_response = await yookassa_client.create_payment(
                amount=float(order.total),
                description=description,
                order_id=str(order.id),
                metadata={"order_id": str(order.id)},
                return_url=return_url,
                cancel_url=cancel_url,
            )

            payment = Payment(
                order_id=order.id,
                yookassa_payment_id=yookassa_response.get("id"),
                amount=float(order.total),
                currency=yookassa_response.get("amount", {}).get(
                    "currency", "RUB"
                ),
                status=PaymentStatus(
                    yookassa_response.get("status", "pending")
                ),
                is_test=yookassa_response.get("test", False),
                confirmation_url=yookassa_response.get(
                    "confirmation", {}
                ).get("confirmation_url"),
            )

            self.payment_repo.session.add(payment)
            await self.payment_repo.session.commit()
            await self.payment_repo.session.refresh(payment)

            logger.info(
                f"Payment created for order {order_id}: {payment.id}"
            )
            return payment

        except YooKassaAPIError as e:
            logger.error(
                f"Failed to create payment for order {order_id}: {e}"
            )
            payment = Payment(
                order_id=order.id,
                amount=float(order.total),
                status=PaymentStatus.CANCELED,
                error_message=str(e),
            )
            self.payment_repo.session.add(payment)
            await self.payment_repo.session.commit()
            raise

    async def poll_payment_status(self, order_id: UUID) -> Payment:
        """
        Проверяет статус платежа через API ЮKassa.
        Используется вместо webhook для тестирования.
        """
        payment = await self.payment_repo.get_by_order_id(order_id)
        if not payment or not payment.yookassa_payment_id:
            raise PaymentNotFoundError()

        if payment.status in [
            PaymentStatus.SUCCEEDED,
            PaymentStatus.CANCELED
        ]:
            return payment

        try:
            yookassa_data = await yookassa_client.get_payment(
                payment.yookassa_payment_id
            )
            new_status = yookassa_data.get("status")

            if new_status and new_status != payment.status.value:
                try:
                    payment.status = PaymentStatus(new_status)
                except ValueError:
                    logger.warning(f"Unknown payment status: {new_status}")

                payment_method_data = yookassa_data.get("payment_method")
                if payment_method_data:
                    method_type = payment_method_data.get("type")
                    if method_type:
                        try:
                            payment.payment_method = PaymentMethod(
                                method_type
                            )
                        except ValueError:
                            pass

                if new_status == "canceled":
                    cancellation_details = yookassa_data.get(
                        "cancellation_details", {}
                    )
                    payment.cancellation_reason = cancellation_details.get(
                        "reason"
                    )
                    payment.cancellation_party = cancellation_details.get(
                        "party"
                    )

                await self.payment_repo.session.commit()
                await self.payment_repo.session.refresh(payment)

                if new_status == "succeeded":
                    await self._update_order_status(
                        payment.order_id, OrderStatus.PROCESSING
                    )
                elif new_status == "canceled":
                    await self._update_order_status(
                        payment.order_id, OrderStatus.CANCELLED
                    )

                logger.info(
                    f"Payment {payment.id} status updated to {new_status}"
                )

            return payment

        except YooKassaAPIError as e:
            logger.error(f"Failed to poll payment status: {e}")
            return payment

    async def _update_order_status(
        self, order_id: UUID, new_status: OrderStatus
    ):
        """Обновляет статус заказа."""
        order = await self.order_repo.read_by_id(order_id)
        if order:
            order.status = new_status
            await self.order_repo.session.commit()
            logger.info(
                f"Order {order_id} status updated to {new_status}"
            )

    async def get_order_payments(self, order_id: UUID) -> list[Payment]:
        """Возвращает все платежи для заказа."""
        return await self.payment_repo.get_order_payments(order_id)

    async def cancel_payment(self, payment_id: UUID) -> Payment:
        """Отменяет платеж."""
        payment = await self.payment_repo.read_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundError()

        if payment.status not in [
            PaymentStatus.PENDING,
            PaymentStatus.WAITING_FOR_CAPTURE
        ]:
            raise InvalidPaymentStatusError(
                f"Cannot cancel payment in status {payment.status}"
            )

        try:
            await yookassa_client.cancel_payment(
                payment.yookassa_payment_id
            )
            payment.status = PaymentStatus.CANCELED
            payment.cancellation_party = "merchant"
            await self.payment_repo.session.commit()
            await self.payment_repo.session.refresh(payment)

            await self._update_order_status(
                payment.order_id, OrderStatus.CANCELLED
            )

            return payment
        except YooKassaAPIError as e:
            logger.error(f"Failed to cancel payment: {e}")
            raise
