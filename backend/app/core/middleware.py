from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import secrets
import hmac


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Пути, которые НЕ требуют CSRF-токена (публичные эндпоинты)
        exempt_paths = [
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/guest",
            "/docs",
            "/openapi.json",
            "/health",
        ]

        # Проверяем, нужно ли применять CSRF для этого пути
        is_exempt = any(request.url.path.startswith(path) for path in exempt_paths)

        # Для небезопасных методов и НЕ исключённых путей
        if request.method in ["POST", "PUT", "DELETE", "PATCH"] and not is_exempt:
            csrf_token_header = request.headers.get("X-CSRF-Token")
            csrf_token_cookie = request.cookies.get("csrf_token")

            if not csrf_token_header or not csrf_token_cookie:
                raise HTTPException(status_code=403, detail="CSRF token missing")
            if not hmac.compare_digest(csrf_token_header, csrf_token_cookie):
                raise HTTPException(status_code=403, detail="CSRF token invalid")

        # Для GET-запросов: если CSRF-токена нет, генерируем и устанавливаем
        if request.method == "GET" and not request.cookies.get("csrf_token"):
            csrf_token = secrets.token_urlsafe(32)
            response = await call_next(request)
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=False,
                secure=True,
                samesite="lax"
            )
            return response

        response = await call_next(request)
        return response