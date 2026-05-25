from fastapi import APIRouter, Depends
from app.auth.schemas import LoginRequest, TokenResponse, RegisterRequest
from app.auth.dependencies import UserServiceDep
from app.auth.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, user_svc: UserServiceDep):
    auth_svc = AuthService(user_svc)
    await auth_svc.register(data)
    token = await auth_svc.authenticate(data.email, data.password)
    return {"access_token": token}

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, user_svc: UserServiceDep):
    auth_svc = AuthService(user_svc)
    token = await auth_svc.authenticate(data.email, data.password)
    return {"access_token": token}
