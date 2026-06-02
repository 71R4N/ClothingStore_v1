from typing import Optional
from uuid import UUID
from app.core.repository import SqlAlchemyRepo
from app.wishlist.models import Wishlist
from sqlalchemy import select, delete


class WishlistRepo(SqlAlchemyRepo):
    model = Wishlist

    async def add_to_wishlist(
        self,
        variant_id: int,
        user_id: UUID | None = None,
        session_id: str | None = None
    ) -> Wishlist:
        new_item = Wishlist(
            variant_id=variant_id,
            user_id=user_id,
            session_id=session_id
        )
        self.session.add(new_item)
        await self.session.commit()
        await self.session.refresh(new_item)
        return new_item

    async def get_user_wishlist(self, user_id: UUID):
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_session_wishlist(self, session_id: str):
        stmt = select(self.model).where(self.model.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_item(
        self,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
        variant_id: Optional[int] = None
    ) -> Wishlist | None:
        stmt = select(self.model).where(self.model.variant_id == variant_id)
        if user_id:
            stmt = stmt.where(self.model.user_id == user_id)
        if session_id:
            stmt = stmt.where(self.model.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def remove_item(
        self,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
        variant_id: Optional[int] = None
    ):
        stmt = delete(self.model).where(self.model.variant_id == variant_id)
        if user_id:
            stmt = stmt.where(self.model.user_id == user_id)
        if session_id:
            stmt = stmt.where(self.model.session_id == session_id)
        await self.session.execute(stmt)
        await self.session.commit()