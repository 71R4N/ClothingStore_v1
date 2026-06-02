from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

PUBLIC_PATHS = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/csrf",
    "/api/v1/auth/logout",
]


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Пропускаем безопасные методы
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)

        # Пропускаем публичные эндпоинты
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # Получаем CSRF из cookie и из заголовка
        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("X-CSRF-Token")

        if not csrf_cookie or not csrf_header:
            raise HTTPException(status_code=403, detail="CSRF token missing")

        if csrf_cookie != csrf_header:
            raise HTTPException(status_code=403, detail="CSRF token invalid")

        return await call_next(request)