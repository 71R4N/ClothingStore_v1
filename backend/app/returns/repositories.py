from app.core.repository import SqlAlchemyRepo
from app.returns.models import Return, ReturnItem, ReturnStatus
from app.orders.models import OrderItem
from app.catalog.models import ProductVariant
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Optional, List


class ReturnRepo(SqlAlchemyRepo):
    """Репозиторий для работы с заявками на возврат."""
    model = Return

    async def get_with_items(self, return_id: UUID) -> Optional[Return]:
        """Получает возврат с жадной загрузкой позиций и товаров."""
        stmt = (
            select(self.model)
            .where(self.model.id == return_id)
            .options(
                selectinload(self.model.items)
                    .selectinload(ReturnItem.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.product),
                selectinload(self.model.items)
                    .selectinload(ReturnItem.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.color),
                selectinload(self.model.items)
                    .selectinload(ReturnItem.order_item)
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
                selectinload(self.model.items)
                    .selectinload(ReturnItem.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.product),
                selectinload(self.model.items)
                    .selectinload(ReturnItem.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.color),
                selectinload(self.model.items)
                    .selectinload(ReturnItem.order_item)
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
        """Подсчитывает общее количество возвратов пользователя."""
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def check_existing_return(
        self,
        order_id: UUID,
        order_item_ids: List[UUID],
        exclude_return_id: Optional[UUID] = None
    ) -> Optional[Return]:
        """Проверяет наличие активной заявки для указанных позиций."""
        stmt = (
            select(self.model)
            .join(ReturnItem)
            .where(
                and_(
                    self.model.order_id == order_id,
                    self.model.status.in_([
                        ReturnStatus.PENDING,
                        ReturnStatus.APPROVED,
                        ReturnStatus.REFUNDED,
                    ]),
                    ReturnItem.order_item_id.in_(order_item_ids),
                )
            )
        )
        if exclude_return_id:
            stmt = stmt.where(self.model.id != exclude_return_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_returns(
        self, skip: int = 0, limit: int = 50
    ) -> List[Return]:
        """Получает список заявок, ожидающих рассмотрения."""
        stmt = (
            select(self.model)
            .where(self.model.status == ReturnStatus.PENDING)
            .options(
                selectinload(self.model.items)
                    .selectinload(ReturnItem.order_item)
                    .selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.product),
            )
            .order_by(self.model.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def create_with_items(
        self,
        return_data: dict,
        items_data: List[dict]
    ) -> Return:
        """Создаёт возврат вместе с позициями в одной транзакции."""
        return_obj = self.model(**return_data)
        self.session.add(return_obj)
        await self.session.flush()

        for item_data in items_data:
            item_data["return_id"] = return_obj.id
            item = ReturnItem(**item_data)
            self.session.add(item)

        await self.session.commit()
        await self.session.refresh(return_obj)
        return return_obj


class ReturnItemRepo(SqlAlchemyRepo):
    """Репозиторий для работы с позициями возврата."""
    model = ReturnItem

    async def get_returned_quantity(
        self, order_item_id: UUID, exclude_return_id: Optional[UUID] = None
    ) -> int:
        """
        Вычисляет суммарное количество товара, уже запрошенного к возврату
        по всем активным заявкам.
        """
        stmt = (
            select(func.coalesce(func.sum(self.model.quantity), 0))
            .join(Return)
            .where(
                and_(
                    self.model.order_item_id == order_item_id,
                    Return.status.in_([
                        ReturnStatus.PENDING,
                        ReturnStatus.APPROVED,
                        ReturnStatus.REFUNDED,
                    ]),
                )
            )
        )
        if exclude_return_id:
            stmt = stmt.where(Return.id != exclude_return_id)

        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)
