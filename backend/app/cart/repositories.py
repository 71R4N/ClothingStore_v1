from sqlalchemy import select, delete, func
from backend.app.core.repository import SQLAlchemyRepo
from backend.app.cart.models import CartItem
from backend.app.cart.schemas import CartItemCreate, CartItemUpdate

class CartRepo(SQLAlchemyRepo[CartItem, CartItemCreate]):
    model = CartItem

    async def get_by_user(self, user_id: int) -> list[CartItem]:
        stmt = select(CartItem).where(CartItem.user_id == user_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_session(self, session_id: str) -> list[CartItem]:
        stmt = select(CartItem).where(CartItem.session_id == session_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_item(self, user_id: int | None, session_id: str | None, product_id: int, size_id: int | None, color_id: int | None) -> CartItem | None:
        conditions = [CartItem.product_id == product_id]
        if user_id:
            conditions.append(CartItem.user_id == user_id)
        elif session_id:
            conditions.append(CartItem.session_id == session_id)
        else:
            return None
        if size_id is not None:
            conditions.append(CartItem.size_id == size_id)
        if color_id is not None:
            conditions.append(CartItem.color_id == color_id)
        stmt = select(CartItem).where(*conditions)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def clear_user_cart(self, user_id: int) -> None:
        await self.session.execute(delete(CartItem).where(CartItem.user_id == user_id))
        await self.session.commit()

    async def clear_session_cart(self, session_id: str) -> None:
        await self.session.execute(delete(CartItem).where(CartItem.session_id == session_id))
        await self.session.commit()
        