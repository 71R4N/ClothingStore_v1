from fastapi import APIRouter, Depends, HTTPException
from backend.app.auth.schemas import LoginRequest, TokenResponse, RefreshTokenRequest
from backend.app.auth.services import AuthService
from backend.app.users.dependencies import get_user_service
from backend.app.users.services import UserService
from backend.app.core.security import create_access_token, create_refresh_token
from jose import jwt, JWTError
from backend.app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    auth_service = AuthService(user_service)
    user = await auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = auth_service.create_tokens(user.id, user.email)
    return tokens

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    try:
        payload = jwt.decode(refresh_data.refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
        email = payload.get("email")
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        new_access = create_access_token(data={"sub": user_id, "email": email})
        new_refresh = create_refresh_token(data={"sub": user_id, "email": email})
        return {"access_token": new_access, "refresh_token": new_refresh}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
