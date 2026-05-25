from app.reviews.repositories import ReviewRepo
from app.reviews.schemas import ReviewCreate, ReviewUpdate
from app.reviews.exceptions import ReviewNotFoundError

class ReviewService:
    def __init__(self, review_repo: ReviewRepo):
        self.review_repo = review_repo

    async def create(self, user_id: str, data: ReviewCreate):
        # Проверить, нет ли уже отзыва
        existing = await self.review_repo.get_user_review_for_product(user_id, data.product_id)
        if existing:
            raise ConflictException("Review already exists for this product")
        review_data = data.model_dump()
        review_data["user_id"] = user_id
        return await self.review_repo.create(ReviewCreate(**review_data))

    async def get_by_id(self, review_id: str):
        review = await self.review_repo.read_by_id(review_id)
        if not review:
            raise ReviewNotFoundError()
        return review

    async def update(self, review_id: str, user_id: str, data: ReviewUpdate):
        review = await self.get_by_id(review_id)
        if str(review.user_id) != user_id:
            raise ForbiddenException("Not your review")
        return await self.review_repo.update(data, review_id, exclude_unset=True)

    async def delete(self, review_id: str, user_id: str):
        review = await self.get_by_id(review_id)
        if str(review.user_id) != user_id and user.role != "admin":
            raise ForbiddenException("Not your review")
        await self.review_repo.delete(review_id)

    async def list_for_product(self, product_id: int, skip: int = 0, limit: int = 20):
        return await self.review_repo.get_product_reviews(product_id, skip, limit)
    