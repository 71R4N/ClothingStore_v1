from fastapi import APIRouter, Response, Request, HTTPException
from app.auth.exceptions import CaptchaRequiredError, InvalidCaptchaError, InvalidCredentialsError
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.auth.dependencies import UserServiceDep
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
    request: Request,
    data: LoginRequest,
    user_svc: UserServiceDep
):
    auth_svc = AuthService(user_svc)
    client_ip = request.client.host
    try:
        token = await auth_svc.authenticate(
            email=data.email,
            password=data.password,
            captcha_response=data.captcha_response,
            client_ip=client_ip
        )
        return {"access_token": token, "token_type": "bearer"}
    except CaptchaRequiredError:
        raise HTTPException(status_code=429, detail="Too many failed attempts. Captcha required.")
    except InvalidCaptchaError:
        raise HTTPException(status_code=400, detail="Invalid captcha")
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
