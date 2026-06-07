from fastapi import APIRouter, Request, Response, Cookie
from app.wishlist.schemas import WishlistCreate, WishlistRead
from app.wishlist.dependencies import WishlistServiceDep
from app.auth.dependencies import OptionalUserDep, CurrentUserDep
from uuid import UUID


router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("/", response_model=list[WishlistRead])
async def get_wishlist(
        request: Request,
        current_user: OptionalUserDep,
        wishlist_svc: WishlistServiceDep,
        session_id: str | None = Cookie(None)
):
    if current_user:
        return await wishlist_svc.get_wishlist(user_id=current_user.id)
    elif session_id:
        return await wishlist_svc.get_wishlist(session_id=session_id)
    return []


@router.post("/items", response_model=WishlistRead, status_code=201)
async def add_to_wishlist(
        data: WishlistCreate,
        request: Request,
        current_user: OptionalUserDep,
        wishlist_svc: WishlistServiceDep,
        response: Response,
        session_id: str | None = Cookie(None)
):
    user_id = current_user.id if current_user else None

    if not user_id and not session_id:
        import secrets
        session_id = secrets.token_urlsafe(32)
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=False,
            samesite="lax",
            max_age=30 * 24 * 60 * 60
        )

    return await wishlist_svc.add_item(
        data=data,
        user_id=user_id,
        session_id=session_id
    )


@router.delete("/items/{variant_id}", status_code=204)
async def remove_from_wishlist(
        variant_id: int,
        request: Request,
        current_user: OptionalUserDep,
        wishlist_svc: WishlistServiceDep,
        session_id: str | None = Cookie(None)
):
    user_id = current_user.id if current_user else None

    if not user_id and not session_id:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException()

    await wishlist_svc.remove_item(
        variant_id=variant_id,
        user_id=user_id,
        session_id=session_id
    )
