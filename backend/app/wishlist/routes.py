from fastapi import APIRouter, Depends
from app.wishlist.schemas import WishlistCreate, WishlistRead
from app.wishlist.dependencies import WishlistServiceDep
from app.wishlist.services import WishlistService
from app.auth.dependencies import CurrentUserDep
from typing import Annotated

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

@router.get("/", response_model=list[WishlistRead])
async def get_wishlist(current_user: CurrentUserDep, wishlist_svc: WishlistServiceDep):
    return await wishlist_svc.get_wishlist(str(current_user.id))

@router.post("/items", response_model=WishlistRead, status_code=201)
async def add_to_wishlist(data: WishlistCreate, current_user: CurrentUserDep, wishlist_svc: WishlistServiceDep):
    return await wishlist_svc.add_item(str(current_user.id), data)

@router.delete("/items/{product_id}", status_code=204)
async def remove_from_wishlist(product_id: int, current_user: CurrentUserDep, wishlist_svc: WishlistServiceDep):
    await wishlist_svc.remove_item(str(current_user.id), product_id)
