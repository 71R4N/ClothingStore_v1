from app.core.repository import SqlAlchemyRepo
from app.orders.models import Order, OrderItem, PaymentTransaction, Return, Address
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class OrderRepo(SqlAlchemyRepo):
    model = Order

    async def get_with_items(self, order_id: str) -> Order | None:
        stmt = select(self.model).where(self.model.id == order_id).options(
            selectinload(self.model.items).selectinload(OrderItem.product),
            selectinload(self.model.shipping_address)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: str, skip: int = 0, limit: int = 20):
        stmt = select(self.model).where(self.model.user_id == user_id).options(
            selectinload(self.model.items)
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

class OrderItemRepo(SqlAlchemyRepo):
    model = OrderItem

class PaymentRepo(SqlAlchemyRepo):
    model = PaymentTransaction

class ReturnRepo(SqlAlchemyRepo):
    model = Return

class AddressRepo(SqlAlchemyRepo):
    model = Address
    