from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from starlette.responses import JSONResponse

PUBLIC_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/csrf",
    "/api/v1/auth/logout",
}

# Пути, которые полностью обходят CSRF-проверку
ADMIN_PATHS_PREFIX = "/admin"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class CSRFMiddleware:
    """
    Pure ASGI middleware для проверки CSRF-токена.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Пропускаем безопасные методы
        if scope["method"] in SAFE_METHODS:
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = request.url.path

        # Пропускаем публичные эндпоинты
        if path in PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return

        # Пропускаем запросы к админ-панели SQLAdmin
        if path.startswith(ADMIN_PATHS_PREFIX):
            await self.app(scope, receive, send)
            return

        # Получаем CSRF из cookie и из заголовка
        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("X-CSRF-Token")

        if not csrf_cookie or not csrf_header:
            response = JSONResponse(
                status_code=403,
                content={"detail": "CSRF token missing"}
            )
            await response(scope, receive, send)
            return

        if csrf_cookie != csrf_header:
            response = JSONResponse(
                status_code=403,
                content={"detail": "CSRF token invalid"}
            )
            await response(scope, receive, send)
            return

        # Всё ок — передаём дальше
        await self.app(scope, receive, send)
