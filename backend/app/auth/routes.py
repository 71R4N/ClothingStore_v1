from fastapi import APIRouter, Depends, Request, Response, HTTPException
from app.auth.schemas import LoginRequest, TokenResponse, RegisterRequest
from app.auth.dependencies import UserServiceDep
from app.auth.services import AuthService
from app.auth.exceptions import CaptchaRequiredError, InvalidCaptchaError, InvalidCredentialsError
from app.core.security import create_access_token, create_refresh_token
from app.users.services import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
        response: Response,
        data: RegisterRequest,
        user_svc: UserServiceDep
):
    auth_svc = AuthService(user_svc)
    user_id = await auth_svc.register(data)
    # После регистрации сразу аутентифицируем
    user = await user_svc.get_by_id(user_id)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Для localhost оставляем False, для продакшена True
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 дней
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
async def login(
        request: Request,
        response: Response,
        data: LoginRequest,
        user_svc: UserServiceDep
):
    auth_svc = AuthService(user_svc)
    client_ip = request.client.host
    try:
        user = await user_svc.get_by_email(data.email)
        if not user:
            raise InvalidCredentialsError()

        # Вызываем authenticate, который проверяет пароль и капчу
        # (он возвращает только access_token, но нам нужен ещё и user)
        access_token = await auth_svc.authenticate(
            email=data.email,
            password=data.password,
            captcha_response=data.captcha_response,
            client_ip=client_ip
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except CaptchaRequiredError:
        raise HTTPException(status_code=429, detail="Too many failed attempts. Captcha required.")
    except InvalidCaptchaError:
        raise HTTPException(status_code=400, detail="Invalid captcha")
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
        request: Request,
        response: Response
):
    # Читаем refresh_token из cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = decode_refresh_token(refresh_token)  # нужно реализовать
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

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
