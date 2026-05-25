from app.core.repository import SqlAlchemyRepo
from app.wishlist.models import Wishlist
from sqlalchemy import select, delete

class WishlistRepo(SqlAlchemyRepo):
    model = Wishlist

    async def get_user_wishlist(self, user_id: str):
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_item(self, user_id: str, product_id: int) -> Wishlist | None:
        stmt = select(self.model).where(self.model.user_id == user_id, self.model.product_id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def remove_item(self, user_id: str, product_id: int):
        stmt = delete(self.model).where(self.model.user_id == user_id, self.model.product_id == product_id)
        await self.session.execute(stmt)
        await self.session.commit()
        