import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone, timedelta
from app.returns.repositories import ReturnRepo
from app.returns.schemas import ReturnCreate
from app.returns.models import Return, ReturnStatus, ReturnReasonType
from app.returns.exceptions import (
    ReturnNotFoundError,
    OrderNotDeliveredError,
    ReturnPeriodExceededError,
    ReturnAlreadyExistsError,
    InvalidReturnQuantityError,
    InvalidReturnStatusTransitionError,
    ReturnLimitExceededError,
)
from app.orders.repositories import OrderRepo, OrderItemRepo
from app.orders.models import Order, OrderStatus
from app.catalog.repositories import ProductVariantRepo
from app.core.exceptions import ForbiddenException

logger = logging.getLogger(__name__)
RETURN_PERIOD_DAYS = 14
MAX_RETURNS_PER_MONTH = 10


class ReturnService:
    """Сервис для работы с индивидуальными заявками на возврат."""

    def __init__(
            self,
            return_repo: ReturnRepo,
            order_repo: OrderRepo,
            order_item_repo: OrderItemRepo,
            variant_repo: ProductVariantRepo,
    ):
        self.return_repo = return_repo
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo
        self.variant_repo = variant_repo

    async def create_return_request(
            self,
            user_id: Optional[UUID],
            guest_email: Optional[str],
            data: ReturnCreate,
    ) -> Return:
        """
        Создаёт заявку на возврат одного товара с полной валидацией.
        """
        # 1. Получаем заказ
        order = await self.order_repo.get_with_items(data.order_id)
        if not order:
            from app.orders.exceptions import OrderNotFoundError
            raise OrderNotFoundError()

        # 2. Проверка прав доступа
        if user_id and order.user_id and order.user_id != user_id:
            raise ForbiddenException(
                detail="Cannot create return for another user's order"
            )
        if not user_id and not guest_email:
            raise ForbiddenException(
                detail="Guest email required for guest returns"
            )

        # 3. Проверка статуса заказа
        if order.status != OrderStatus.DELIVERED:
            raise OrderNotDeliveredError()

        # 4. Проверка срока возврата (14 дней)
        delivery_date = order.updated_at or order.created_at
        if delivery_date.tzinfo is None:
            delivery_date = delivery_date.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if now - delivery_date > timedelta(days=RETURN_PERIOD_DAYS):
            raise ReturnPeriodExceededError()

        # 5. Лимит возвратов для пользователя
        if user_id:
            returns_count = await self.return_repo.count_user_returns(user_id)
            if returns_count >= MAX_RETURNS_PER_MONTH:
                raise ReturnLimitExceededError(
                    detail=f"Monthly return limit ({MAX_RETURNS_PER_MONTH}) exceeded"
                )

        # 6. Поиск конкретной позиции заказа
        order_item = None
        for item in order.items:
            if item.id == data.order_item_id:
                order_item = item
                break

        if not order_item:
            raise InvalidReturnQuantityError(
                detail=f"Order item {data.order_item_id} not found in order"
            )

        # 7. Проверка дубликатов для конкретной позиции
        existing = await self.return_repo.check_existing_return_for_item(
            data.order_item_id
        )
        if existing:
            raise ReturnAlreadyExistsError()

        # 8. Проверка доступного количества
        already_returned = await self.return_repo.get_returned_quantity_for_item(
            data.order_item_id
        )
        available = order_item.quantity - already_returned
        if data.quantity > available:
            raise InvalidReturnQuantityError(
                detail=f"Cannot return {data.quantity} units. Available: {available}"
            )

        # 9. Расчёт суммы возврата
        refund_amount = float(order_item.price_at_purchase) * data.quantity

        # 10. Создание возврата
        return_obj = Return(
            order_id=data.order_id,
            order_item_id=data.order_item_id,
            user_id=user_id,
            guest_email=guest_email,
            reason_type=ReturnReasonType(data.reason_type.value),
            description=data.description,
            quantity=data.quantity,
            refund_amount=refund_amount,
            photos=data.photos,
            status=ReturnStatus.PENDING,
        )

        self.return_repo.session.add(return_obj)
        await self.return_repo.session.commit()
        await self.return_repo.session.refresh(return_obj)

        logger.info(
            f"Return request created: {return_obj.id} for order item "
            f"{data.order_item_id}, amount: {refund_amount}"
        )
        return return_obj

    async def get_return(self, return_id: UUID) -> Return:
        """Получает возврат по ID с жадной загрузкой."""
        return_obj = await self.return_repo.get_with_item_details(return_id)
        if not return_obj:
            raise ReturnNotFoundError()
        return return_obj

    async def get_user_returns(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 20
    ) -> tuple[List[Return], int]:
        """Возвращает список возвратов пользователя."""
        items = await self.return_repo.get_user_returns(user_id, skip, limit)
        total = await self.return_repo.count_user_returns(user_id)
        return items, total

    async def cancel_return(self, return_id: UUID, user_id: UUID) -> Return:
        """Отменяет заявку на возврат."""
        return_obj = await self.get_return(return_id)
        if return_obj.user_id != user_id:
            raise ForbiddenException(
                detail="Cannot cancel another user's return"
            )
        if return_obj.status != ReturnStatus.PENDING:
            raise InvalidReturnStatusTransitionError(
                detail=f"Cannot cancel return in status {return_obj.status}"
            )
        return_obj.status = ReturnStatus.CANCELLED
        return_obj.updated_at = datetime.utcnow()
        await self.return_repo.session.commit()
        await self.return_repo.session.refresh(return_obj)
        logger.info(f"Return {return_id} cancelled by user {user_id}")
        return return_obj

    async def approve_return(
            self,
            return_id: UUID,
            admin_id: UUID,
    ) -> Return:
        """
        Одобряет заявку: возвращает товары на склад и инициирует возврат средств.
        """
        return_obj = await self.get_return(return_id)
        if return_obj.status != ReturnStatus.PENDING:
            raise InvalidReturnStatusTransitionError(
                detail=f"Cannot approve return in status {return_obj.status}"
            )

        # Возвращаем товары на склад
        if return_obj.order_item and return_obj.order_item.variant_id:
            variant = await self.variant_repo.read_by_id(
                return_obj.order_item.variant_id
            )
            if variant:
                variant.stock_quantity += return_obj.quantity
                logger.info(
                    f"Restocked {return_obj.quantity} units of variant "
                    f"{return_obj.order_item.variant_id}"
                )

        # Обновляем статус
        return_obj.status = ReturnStatus.APPROVED
        return_obj.resolved_at = datetime.utcnow()
        return_obj.resolved_by = admin_id
        return_obj.updated_at = datetime.utcnow()
        await self.return_repo.session.commit()
        await self.return_repo.session.refresh(return_obj)

        # Запускаем асинхронный возврат средств
        try:
            from worker.tasks.returns import process_refund_task
            process_refund_task.delay(
                str(return_obj.id), float(return_obj.refund_amount)
            )
            logger.info(
                f"Refund task queued for return {return_obj.id}, "
                f"amount: {return_obj.refund_amount}"
            )
        except Exception as e:
            logger.error(f"Failed to queue refund task: {e}")

        return return_obj

    async def reject_return(
            self,
            return_id: UUID,
            admin_id: UUID,
            rejection_reason: str,
    ) -> Return:
        """Отклоняет заявку на возврат."""
        return_obj = await self.get_return(return_id)
        if return_obj.status != ReturnStatus.PENDING:
            raise InvalidReturnStatusTransitionError(
                detail=f"Cannot reject return in status {return_obj.status}"
            )
        return_obj.status = ReturnStatus.REJECTED
        return_obj.resolved_at = datetime.utcnow()
        return_obj.resolved_by = admin_id
        return_obj.rejection_reason = rejection_reason
        return_obj.updated_at = datetime.utcnow()
        await self.return_repo.session.commit()
        await self.return_repo.session.refresh(return_obj)
        logger.info(f"Return {return_id} rejected by admin {admin_id}")
        return return_obj

    async def mark_refunded(
            self, return_id: UUID, refund_payment_id: str
    ) -> Return:
        """Отмечает возврат как оплаченный."""
        return_obj = await self.get_return(return_id)
        return_obj.status = ReturnStatus.REFUNDED
        return_obj.refund_payment_id = refund_payment_id
        return_obj.updated_at = datetime.utcnow()
        await self.return_repo.session.commit()
        await self.return_repo.session.refresh(return_obj)
        return return_obj

    async def mark_failed(self, return_id: UUID, error: str) -> Return:
        """Отмечает возврат как неуспешный."""
        return_obj = await self.get_return(return_id)
        return_obj.status = ReturnStatus.FAILED
        return_obj.rejection_reason = f"Refund failed: {error}"
        return_obj.updated_at = datetime.utcnow()
        await self.return_repo.session.commit()
        await self.return_repo.session.refresh(return_obj)
        return return_obj

    async def get_pending_returns(
            self, skip: int = 0, limit: int = 50
    ) -> List[Return]:
        """Возвращает список заявок, ожидающих рассмотрения."""
        return await self.return_repo.get_pending_returns(skip, limit)
