from app.core.repository import SqlAlchemyRepo
from app.reviews.models import Review
from sqlalchemy import select

class ReviewRepo(SqlAlchemyRepo):
    model = Review

    async def get_product_reviews(self, product_id: int, skip: int = 0, limit: int = 20):
        stmt = select(self.model).where(self.model.product_id == product_id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_review_for_product(self, user_id: str, product_id: int) -> Review | None:
        stmt = select(self.model).where(self.model.user_id == user_id, self.model.product_id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    