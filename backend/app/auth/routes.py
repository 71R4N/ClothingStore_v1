from fastapi import APIRouter, Depends, Response
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.auth.dependencies import UserServiceDep
from app.auth.exceptions import InvalidCredentialsError
from app.auth.services import AuthService
from app.core.security import create_access_token, create_refresh_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
        response: Response,
        data: RegisterRequest,
        user_svc: UserServiceDep
):
    auth_svc = AuthService(user_svc)
    user_id = await auth_svc.register(data)
    user = await user_svc.get_by_id(user_id)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 дней
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
async def login(
        response: Response,
        data: LoginRequest,
        user_svc: UserServiceDep
):
    auth_svc = AuthService(user_svc)
    user = await user_svc.get_by_email(data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise InvalidCredentialsError()

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    return {"access_token": access_token, "token_type": "bearer"}
