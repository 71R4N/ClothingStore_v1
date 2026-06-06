import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone, timedelta

from app.returns.repositories import ReturnRepo, ReturnItemRepo
from app.returns.schemas import ReturnCreate
from app.returns.models import Return, ReturnItem, ReturnStatus, ReturnReasonType
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
from app.catalog.models import ProductVariant
from app.core.exceptions import ForbiddenException

logger = logging.getLogger(__name__)

RETURN_PERIOD_DAYS = 14
MAX_RETURNS_PER_MONTH = 10


class ReturnService:
    """Сервис для работы с возвратами товаров."""

    def __init__(
        self,
        return_repo: ReturnRepo,
        return_item_repo: ReturnItemRepo,
        order_repo: OrderRepo,
        order_item_repo: OrderItemRepo,
        variant_repo: ProductVariantRepo,
    ):
        self.return_repo = return_repo
        self.return_item_repo = return_item_repo
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
        Создаёт заявку на возврат с полной валидацией бизнес-правил.
        """
        # 1. Получаем заказ с жадной загрузкой позиций
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

        # 6. Валидация позиций и проверка дубликатов
        order_item_ids = [item.order_item_id for item in data.items]
        existing = await self.return_repo.check_existing_return(
            data.order_id, order_item_ids
        )
        if existing:
            raise ReturnAlreadyExistsError()

        # 7. Построение карты order_item_id -> OrderItem
        order_items_map = {str(item.id): item for item in order.items}

        # 8. Валидация каждой позиции и расчёт суммы
        total_amount = 0.0
        items_data = []

        for item in data.items:
            order_item = order_items_map.get(str(item.order_item_id))
            if not order_item:
                raise InvalidReturnQuantityError(
                    detail=f"Order item {item.order_item_id} not found in order"
                )

            # Проверяем, сколько уже запрошено к возврату
            already_returned = await self.return_item_repo.get_returned_quantity(
                item.order_item_id
            )
            available = order_item.quantity - already_returned

            if item.quantity > available:
                raise InvalidReturnQuantityError(
                    detail=f"Cannot return {item.quantity} units. "
                           f"Available: {available}"
                )

            refund_amount = float(order_item.price_at_purchase) * item.quantity
            total_amount += refund_amount

            items_data.append({
                "order_item_id": item.order_item_id,
                "variant_id": order_item.variant_id,
                "quantity": item.quantity,
                "refund_amount": refund_amount,
                "photos": item.photos,
            })

        # 9. Создание возврата
        return_data = {
            "order_id": data.order_id,
            "user_id": user_id,
            "guest_email": guest_email,
            "reason_type": ReturnReasonType(data.reason_type.value),
            "description": data.description,
            "total_amount": total_amount,
            "status": ReturnStatus.PENDING,
        }

        return_obj = await self.return_repo.create_with_items(
            return_data, items_data
        )

        logger.info(
            f"Return request created: {return_obj.id} for order {data.order_id}, "
            f"amount: {total_amount}"
        )
        return return_obj

    async def get_return(self, return_id: UUID) -> Return:
        """Получает возврат по ID с жадной загрузкой."""
        return_obj = await self.return_repo.get_with_items(return_id)
        if not return_obj:
            raise ReturnNotFoundError()
        return return_obj

    async def get_user_returns(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Return], int]:
        """Возвращает список возвратов пользователя с общим количеством."""
        items = await self.return_repo.get_user_returns(user_id, skip, limit)
        total = await self.return_repo.count_user_returns(user_id)
        return items, total

    async def cancel_return(self, return_id: UUID, user_id: UUID) -> Return:
        """Отменяет заявку на возврат (только пользователь-владелец)."""
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
        Одобряет заявку на возврат:
        1. Возвращает товары на склад
        2. Инициирует возврат средств через Celery
        """
        return_obj = await self.get_return(return_id)

        if return_obj.status != ReturnStatus.PENDING:
            raise InvalidReturnStatusTransitionError(
                detail=f"Cannot approve return in status {return_obj.status}"
            )

        # Возвращаем товары на склад
        for item in return_obj.items:
            if item.variant_id:
                variant = await self.variant_repo.read_by_id(item.variant_id)
                if variant:
                    variant.stock_quantity += item.quantity
                    logger.info(
                        f"Restocked {item.quantity} units of variant "
                        f"{item.variant_id}"
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
            process_refund_task.delay(str(return_obj.id), float(return_obj.total_amount))
            logger.info(
                f"Refund task queued for return {return_obj.id}, "
                f"amount: {return_obj.total_amount}"
            )
        except Exception as e:
            logger.error(f"Failed to queue refund task: {e}")
            # Возврат средств будет обработан вручную администратором

        return return_obj

    async def reject_return(
        self,
        return_id: UUID,
        admin_id: UUID,
        rejection_reason: str,
    ) -> Return:
        """Отклоняет заявку на возврат с указанием причины."""
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
        """Отмечает возврат как оплаченный после успешного refund."""
        return_obj = await self.get_return(return_id)
        return_obj.status = ReturnStatus.REFUNDED
        return_obj.refund_payment_id = refund_payment_id
        return_obj.updated_at = datetime.utcnow()

        await self.return_repo.session.commit()
        await self.return_repo.session.refresh(return_obj)

        logger.info(
            f"Return {return_id} marked as refunded: {refund_payment_id}"
        )
        return return_obj

    async def mark_failed(self, return_id: UUID, error: str) -> Return:
        """Отмечает возврат как неуспешный при ошибке refund."""
        return_obj = await self.get_return(return_id)
        return_obj.status = ReturnStatus.FAILED
        return_obj.rejection_reason = f"Refund failed: {error}"
        return_obj.updated_at = datetime.utcnow()

        await self.return_repo.session.commit()
        await self.return_repo.session.refresh(return_obj)

        logger.error(f"Return {return_id} refund failed: {error}")
        return return_obj

    async def get_pending_returns(
        self, skip: int = 0, limit: int = 50
    ) -> List[Return]:
        """Возвращает список заявок, ожидающих рассмотрения."""
        return await self.return_repo.get_pending_returns(skip, limit)
