from app.core.repository import SqlAlchemyRepo
from app.orders.models import Order, OrderItem, OrderStatus
from app.catalog.models import ProductVariant
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID


class OrderRepo(SqlAlchemyRepo):
    model = Order

    async def get_with_items(self, order_id: UUID) -> Order | None:
        """Получает заказ с жадной загрузкой позиций, вариантов и возвратов."""
        stmt = select(self.model).where(self.model.id == order_id).options(
            selectinload(self.model.items)
            .selectinload(OrderItem.variant)
            .selectinload(ProductVariant.product),
            selectinload(self.model.items)
            .selectinload(OrderItem.variant)
            .selectinload(ProductVariant.color),
            selectinload(self.model.items)
            .selectinload(OrderItem.variant)
            .selectinload(ProductVariant.size),
            # Жадная загрузка индивидуальных заявок на возврат
            selectinload(self.model.items).selectinload(OrderItem.returns),
        ).execution_options(populate_existing=True)  # Принудительное обновление связей

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: UUID, skip: int = 0, limit: int = 20):
        """Получает список заказов пользователя."""
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(
                selectinload(self.model.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.product),
                selectinload(self.model.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.color),
                selectinload(self.model.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.size),
                selectinload(self.model.items).selectinload(OrderItem.returns),
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).execution_options(populate_existing=True)

        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def get_user_orders_by_group(
            self,
            user_id: UUID,
            status_group: str = "all",
            skip: int = 0,
            limit: int = 20
    ):
        """Получает заказы пользователя с фильтрацией по группе статусов."""
        status_filters = {
            "active": [OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.SHIPPED],
            "history": [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            "all": None
        }
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(
                selectinload(self.model.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.product),
                selectinload(self.model.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.color),
                selectinload(self.model.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.size),
                selectinload(self.model.items).selectinload(OrderItem.returns),
            )
            .order_by(self.model.created_at.desc())
        )
        if status_group in status_filters and status_filters[status_group] is not None:
            stmt = stmt.where(self.model.status.in_(status_filters[status_group]))

        stmt = stmt.offset(skip).limit(limit).execution_options(populate_existing=True)

        result = await self.session.execute(stmt)
        return result.scalars().unique().all()


class OrderItemRepo(SqlAlchemyRepo):
    model = OrderItem
