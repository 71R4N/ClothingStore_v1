# backend/worker/tasks/returns.py
import asyncio
import logging
from uuid import UUID
from worker.celery_app import celery
from app.core.database import AsyncSessionLocal
from app.returns.repositories import ReturnRepo
from app.returns.services import ReturnService
from app.returns.models import ReturnStatus
from app.orders.repositories import OrderRepo, OrderItemRepo
from app.catalog.repositories import ProductVariantRepo
from app.payments.client import yookassa_client, YooKassaAPIError
from app.payments.repositories import PaymentRepo

logger = logging.getLogger(__name__)


async def _process_refund_async(return_id: UUID, amount: float):
    """Асинхронная логика возврата средств."""
    async with AsyncSessionLocal() as session:
        return_repo = ReturnRepo(session)
        order_repo = OrderRepo(session)
        order_item_repo = OrderItemRepo(session)
        variant_repo = ProductVariantRepo(session)
        payment_repo = PaymentRepo(session)

        service = ReturnService(
            return_repo=return_repo,
            order_repo=order_repo,
            order_item_repo=order_item_repo,
            variant_repo=variant_repo,
        )

        return_obj = await return_repo.get_with_item_details(return_id)
        if not return_obj:
            logger.error(f"Return {return_id} not found for refund")
            return

        if return_obj.status != ReturnStatus.APPROVED:
            logger.warning(
                f"Return {return_id} is not approved "
                f"(status: {return_obj.status})"
            )
            return

        # Находим успешный платёж для заказа
        payment = await payment_repo.get_by_order_id(return_obj.order_id)
        if not payment or not payment.yookassa_payment_id:
            error_msg = "No successful payment found for order"
            logger.error(f"{error_msg}: {return_obj.order_id}")
            await service.mark_failed(return_id, error_msg)
            return

        # Вызываем ЮKassa Refund API
        try:
            refund_result = await yookassa_client.create_refund(
                payment_id=payment.yookassa_payment_id,
                amount=amount,
                description=f"Refund for return {str(return_id)[:8]}"
            )
            yookassa_refund_id = refund_result.get("id")
            refund_status = refund_result.get("status")

            if refund_status == "succeeded":
                await service.mark_refunded(return_id, yookassa_refund_id)
                logger.info(
                    f"Refund succeeded for return {return_id}: "
                    f"{yookassa_refund_id}"
                )
            else:
                return_obj.refund_payment_id = yookassa_refund_id
                await session.commit()
                logger.info(
                    f"Refund pending for return {return_id}: "
                    f"{yookassa_refund_id}"
                )

        except YooKassaAPIError as e:
            logger.error(f"YooKassa refund failed: {e}")
            raise


async def _mark_refund_failed(return_id: UUID, error: str):
    """Отмечает возврат как failed при превышении retry."""
    async with AsyncSessionLocal() as session:
        return_repo = ReturnRepo(session)
        order_repo = OrderRepo(session)
        order_item_repo = OrderItemRepo(session)
        variant_repo = ProductVariantRepo(session)

        service = ReturnService(
            return_repo=return_repo,
            order_repo=order_repo,
            order_item_repo=order_item_repo,
            variant_repo=variant_repo,
        )
        await service.mark_failed(return_id, error)


@celery.task(
    name="worker.tasks.returns.process_refund_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def process_refund_task(self, return_id: str, amount: float):
    """
    Celery-задача для асинхронного возврата средств через YooKassa.
    Повторяется до 3 раз при ошибках.
    """
    logger.info(
        f"Starting refund task for return {return_id}, amount: {amount}"
    )
    try:
        asyncio.run(_process_refund_async(UUID(return_id), amount))
    except Exception as e:
        logger.error(
            f"Refund task failed for return {return_id}: "
            f"{type(e).__name__}: {e}"
        )
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(
                f"Max retries exceeded for return {return_id}, "
                f"marking as failed"
            )
            asyncio.run(
                _mark_refund_failed(UUID(return_id), str(e))
            )
