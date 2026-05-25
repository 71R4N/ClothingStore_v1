from app.wishlist.repositories import WishlistRepo
from app.wishlist.schemas import WishlistCreate

class WishlistService:
    def __init__(self, repo: WishlistRepo):
        self.repo = repo

    async def add_item(self, user_id: str, data: WishlistCreate):
        existing = await self.repo.find_item(user_id, data.product_id)
        if existing:
            return existing
        return await self.repo.create(WishlistCreate(user_id=user_id, **data.model_dump()))

    async def get_wishlist(self, user_id: str):
        return await self.repo.get_user_wishlist(user_id)

    async def remove_item(self, user_id: str, product_id: int):
        await self.repo.remove_item(user_id, product_id)
        