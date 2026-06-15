from app.core.repository import SqlAlchemyRepo
from app.cart.models import CartItem
from app.catalog.models import ProductVariant
from sqlalchemy import select, delete, and_, or_
from sqlalchemy.orm import selectinload
from uuid import UUID


class CartRepo(SqlAlchemyRepo):
    model = CartItem

    async def create_item(self, **kwargs) -> CartItem:
        item = self.model(**kwargs)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get_user_cart(self, user_id: UUID) -> list[CartItem]:
        stmt = select(self.model).where(
            self.model.user_id == user_id
        ).options(
            selectinload(self.model.variant).selectinload(ProductVariant.product),
            selectinload(self.model.variant).selectinload(ProductVariant.color),
            selectinload(self.model.variant).selectinload(ProductVariant.size),
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def get_session_cart(self, session_id: str) -> list[CartItem]:
        stmt = select(self.model).where(
            self.model.session_id == session_id
        ).options(
            selectinload(self.model.variant).selectinload(ProductVariant.product),
            selectinload(self.model.variant).selectinload(ProductVariant.color),
            selectinload(self.model.variant).selectinload(ProductVariant.size),
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def find_item(
            self,
            user_id: UUID | None,
            session_id: str | None,
            variant_id: int
    ) -> CartItem | None:
        conditions = [self.model.variant_id == variant_id]

        if user_id:
            conditions.append(self.model.user_id == user_id)
        elif session_id:
            conditions.append(self.model.session_id == session_id)
        else:
            return None

        stmt = select(self.model).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def merge_session_cart_to_user(self, user_id: UUID, session_id: str):
        """При авторизации переносим корзину сессии пользователю."""
        session_items = await self.get_session_cart(session_id)

        for item in session_items:
            existing = await self.find_item(user_id, None, item.variant_id)
            if existing:
                existing.quantity += item.quantity
                await self.session.delete(item)
            else:
                item.user_id = user_id
                item.session_id = None

        await self.session.commit()

    async def clear_cart(self, user_id: UUID | None, session_id: str | None):
        conditions = []
        if user_id:
            conditions.append(self.model.user_id == user_id)
        if session_id:
            conditions.append(self.model.session_id == session_id)
        if not conditions:
            return
        stmt = delete(self.model).where(
            or_(*conditions) if len(conditions) > 1 else conditions[0]
        )
        await self.session.execute(stmt)
        await self.session.commit()