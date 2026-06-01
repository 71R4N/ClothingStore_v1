from app.core.repository import SqlAlchemyRepo
from app.cart.models import CartItem
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import selectinload

class CartRepo(SqlAlchemyRepo):
    model = CartItem

    async def create_item(self, **kwargs) -> CartItem:
        item = self.model(**kwargs)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get_user_cart(self, user_id: str) -> list[CartItem]:
        stmt = select(self.model).where(
            self.model.user_id == user_id
        ).options(
            selectinload(self.model.product),
            selectinload(self.model.size),
            selectinload(self.model.color)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_session_cart(self, session_id: str) -> list[CartItem]:
        stmt = select(self.model).where(
            self.model.session_id == session_id
        ).options(
            selectinload(self.model.product),
            selectinload(self.model.size),
            selectinload(self.model.color)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_item(self, user_id: str | None, session_id: str | None,
                        product_id: int, size_id: int | None, color_id: int | None) -> CartItem | None:
        conditions = [self.model.product_id == product_id]
        if user_id:
            conditions.append(self.model.user_id == user_id)
        elif session_id:
            conditions.append(self.model.session_id == session_id)
        if size_id:
            conditions.append(self.model.size_id == size_id)
        if color_id:
            conditions.append(self.model.color_id == color_id)

        stmt = select(self.model).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def merge_session_cart_to_user(self, user_id: str, session_id: str):
        # При авторизации переносим корзину сессии пользователю
        session_items = await self.get_session_cart(session_id)
        for item in session_items:
            existing = await self.find_item(user_id, None, item.product_id, item.size_id, item.color_id)
            if existing:
                existing.quantity += item.quantity
                await self.session.merge(existing)
            else:
                item.user_id = user_id
                item.session_id = None
                await self.session.merge(item)
        # Удаляем оставшиеся с session_id (если не все перенеслись)
        stmt = delete(self.model).where(self.model.session_id == session_id)
        await self.session.execute(stmt)
        await self.session.commit()
        