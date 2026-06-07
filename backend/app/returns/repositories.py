from app.core.repository import SqlAlchemyRepo
from app.returns.models import Return, ReturnStatus
from app.orders.models import OrderItem
from app.catalog.models import ProductVariant
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Optional, List


class ReturnRepo(SqlAlchemyRepo):
    """Репозиторий для работы с индивидуальными заявками на возврат."""
    model = Return

    async def get_with_item_details(self, return_id: UUID) -> Optional[Return]:
        """Получает возврат с жадной загрузкой позиции и товара."""
        stmt = (
            select(self.model)
            .where(self.model.id == return_id)
            .options(
                selectinload(self.model.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.product),
                selectinload(self.model.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.color),
                selectinload(self.model.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.size),
                selectinload(self.model.order),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_returns(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[Return]:
        """Получает список возвратов пользователя."""
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(
                selectinload(self.model.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.product),
                selectinload(self.model.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.color),
                selectinload(self.model.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.size),
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def count_user_returns(self, user_id: UUID) -> int:
        """Подсчитывает количество возвратов пользователя."""
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def check_existing_return_for_item(
        self,
        order_item_id: UUID,
    ) -> Optional[Return]:
        """Проверяет наличие активной заявки для конкретной позиции."""
        stmt = (
            select(self.model)
            .where(
                self.model.order_item_id == order_item_id,
                self.model.status.in_([
                    ReturnStatus.PENDING,
                    ReturnStatus.APPROVED,
                    ReturnStatus.REFUNDED,
                ]),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_returned_quantity_for_item(
        self, order_item_id: UUID
    ) -> int:
        """Вычисляет суммарное количество, запрошенное к возврату."""
        stmt = (
            select(func.coalesce(func.sum(self.model.quantity), 0))
            .where(
                self.model.order_item_id == order_item_id,
                self.model.status.in_([
                    ReturnStatus.PENDING,
                    ReturnStatus.APPROVED,
                    ReturnStatus.REFUNDED,
                ]),
            )
        )
        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)

    async def get_pending_returns(
        self, skip: int = 0, limit: int = 50
    ) -> List[Return]:
        """Получает заявки, ожидающие рассмотрения."""
        stmt = (
            select(self.model)
            .where(self.model.status == ReturnStatus.PENDING)
            .options(
                selectinload(self.model.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.product),
            )
            .order_by(self.model.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()
