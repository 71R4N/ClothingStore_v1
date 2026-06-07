from uuid import UUID
from typing import Optional
from app.wishlist.repositories import WishlistRepo
from app.wishlist.schemas import WishlistCreate
from app.wishlist.models import Wishlist

class WishlistService:
    def __init__(self, repo: WishlistRepo):
        self.repo = repo

    async def add_item(
        self,
        data: WishlistCreate,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None
    ) -> Wishlist:
        existing = await self.repo.find_item(
            user_id=user_id,
            session_id=session_id,
            variant_id=data.variant_id
        )
        if existing:
            return existing
        return await self.repo.add_to_wishlist(
            variant_id=data.variant_id,
            user_id=user_id,
            session_id=session_id
        )

    async def get_wishlist(
        self,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None
    ):
        if user_id:
            return await self.repo.get_user_wishlist(user_id)
        elif session_id:
            return await self.repo.get_session_wishlist(session_id)
        return []

    async def remove_item(
        self,
        variant_id: int,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None
    ):
        if not user_id and not session_id:
            raise ValueError("Необходимо указать либо user_id, либо session_id для удаления товара")
        await self.repo.remove_item(
            user_id=user_id,
            session_id=session_id,
            variant_id=variant_id
        )

    async def clear_session(self, session_id: str):
        """Очищает гостевое избранное при выходе из аккаунта."""
        await self.repo.clear_session_wishlist(session_id)
