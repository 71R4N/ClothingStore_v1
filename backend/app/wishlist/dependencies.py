from typing import Annotated

from fastapi import Depends
from app.core.database import SessionDbDep
from app.wishlist.repositories import WishlistRepo
from app.wishlist.services import WishlistService

def get_wishlist_service(session: SessionDbDep) -> WishlistService:
    return WishlistService(WishlistRepo(session))

WishlistServiceDep = Annotated[WishlistService, Depends(get_wishlist_service)]
