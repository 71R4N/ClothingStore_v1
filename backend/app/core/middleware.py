from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import secrets
import hmac


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Для небезопасных методов (POST, PUT, DELETE, PATCH) проверяем CSRF-токен
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Получаем токен из заголовка X-CSRF-Token
            csrf_token_header = request.headers.get("X-CSRF-Token")
            # Получаем токен из cookie
            csrf_token_cookie = request.cookies.get("csrf_token")

            if not csrf_token_header or not csrf_token_cookie:
                raise HTTPException(status_code=403, detail="CSRF token missing")

            # Сравниваем токены (используем hmac.compare_digest для защиты от timing-атак)
            if not hmac.compare_digest(csrf_token_header, csrf_token_cookie):
                raise HTTPException(status_code=403, detail="CSRF token invalid")

        # Для GET-запросов, если CSRF-токена нет — генерируем и устанавливаем его
        if request.method == "GET" and not request.cookies.get("csrf_token"):
            csrf_token = secrets.token_urlsafe(32)
            request.state.csrf_token = csrf_token
            response = await call_next(request)
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=False,  # Токен должен быть доступен для JS
                secure=True,
                samesite="lax"
            )
            return response

        response = await call_next(request)
        return response