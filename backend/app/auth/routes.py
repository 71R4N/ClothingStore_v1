from fastapi import APIRouter, Request, Response, HTTPException, status, Cookie
from app.auth.schemas import LoginRequest, TokenResponse, RegisterRequest
from app.auth.dependencies import UserServiceDep
from app.auth.services import AuthService
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token, generate_csrf_token
from app.core.config import settings
from app.core.database import SessionDbDep
from app.cart.repositories import CartRepo
from app.wishlist.repositories import WishlistRepo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
        response: Response,
        data: RegisterRequest,
        user_svc: UserServiceDep,
        session_id: str | None = Cookie(None),
        session: SessionDbDep = None,
):
    auth_svc = AuthService(user_svc)
    user_id = await auth_svc.register(data)

    # При регистрации переносим гостевую корзину и избранное в новый аккаунт
    if session_id and session:
        cart_repo = CartRepo(session)
        wishlist_repo = WishlistRepo(session)

        await cart_repo.merge_session_cart_to_user(user_id, session_id)
        await wishlist_repo.merge_session_wishlist_to_user(user_id, session_id)

    user = await user_svc.get_by_id(user_id)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    # Очищаем гостевую сессию после регистрации
    response.delete_cookie("session_id")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/csrf")
async def get_csrf_token(response: Response):
    csrf_token = generate_csrf_token()
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24
    )
    return {"status": "ok"}


@router.post("/login")
async def login(
        response: Response,
        request: Request,
        data: LoginRequest,
        user_svc: UserServiceDep
):
    auth_svc = AuthService(user_svc)
    client_ip = request.client.host if request.client else None
    user = await auth_svc.authenticate(
        email=data.email,
        password=data.password,
        captcha_response=data.captcha_response,
        client_ip=client_ip
    )
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    # При входе в существующий аккаунт НЕ переносим данные из гостевой сессии
    # Просто очищаем гостевую сессию
    response.delete_cookie("session_id")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
        response: Response,
        session_id: str | None = Cookie(None),
        session: SessionDbDep = None,
):
    # При выходе из аккаунта очищаем гостевую корзину и избранное
    if session_id and session:
        cart_repo = CartRepo(session)
        wishlist_repo = WishlistRepo(session)

        await cart_repo.clear_cart(None, session_id)
        await wishlist_repo.clear_session_wishlist(session_id)

    response.delete_cookie("refresh_token")
    response.delete_cookie("csrf_token")
    response.delete_cookie("session_id")
    return {"status": "ok"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
        request: Request,
        response: Response
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    payload = decode_refresh_token(refresh_token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload["sub"]
    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    return {"access_token": new_access_token, "token_type": "bearer"}
