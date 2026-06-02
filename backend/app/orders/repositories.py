from app.core.repository import SqlAlchemyRepo
from app.orders.models import Order, OrderItem
from app.catalog.models import ProductVariant
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID


class OrderRepo(SqlAlchemyRepo):
    model = Order

    async def get_with_items(self, order_id: UUID) -> Order | None:
        stmt = select(self.model).where(self.model.id == order_id).options(
            selectinload(self.model.items).selectinload(OrderItem.variant).selectinload(ProductVariant.product),
            selectinload(self.model.items).selectinload(OrderItem.variant).selectinload(ProductVariant.color),
            selectinload(self.model.items).selectinload(OrderItem.variant).selectinload(ProductVariant.size),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: UUID, skip: int = 0, limit: int = 20):
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(selectinload(self.model.items))
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()


class OrderItemRepo(SqlAlchemyRepo):
    model = OrderItem
