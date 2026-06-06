# backend/app/admin/auth.py
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from app.core.security import decode_access_token, verify_password
from app.users.services import UserService
from app.users.repositories import UserRepo
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from uuid import UUID
from itsdangerous import TimestampSigner, BadSignature
import json


class AdminAuth(AuthenticationBackend):
    """
    Backend аутентификации для SQLAdmin.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        print(f"[ADMIN LOGIN] Attempt for email: {email}")
        print(f"[ADMIN LOGIN] Secret key used: '{settings.SESSION_SECRET_KEY}'")

        if not email or not password:
            print("[ADMIN LOGIN] Failed: empty credentials")
            return False

        async with AsyncSessionLocal() as session:
            user_repo = UserRepo(session)
            user_svc = UserService(user_repo)
            try:
                user = await user_svc.get_by_email(email)
                if not user:
                    print(f"[ADMIN LOGIN] Failed: user {email} not found")
                    return False

                if not verify_password(password, user.password_hash):
                    print(f"[ADMIN LOGIN] Failed: invalid password for {email}")
                    return False

                if user.role != "admin":
                    print(f"[ADMIN LOGIN] Failed: user {email} role is '{user.role}'")
                    return False

                if not user.is_active:
                    print(f"[ADMIN LOGIN] Failed: user {email} is inactive")
                    return False

                request.session.update({"admin_user_id": str(user.id)})
                print(f"[ADMIN LOGIN] Success. Session dict now: {dict(request.session)}")
                return True

            except Exception as e:
                print(f"[ADMIN LOGIN] Exception: {type(e).__name__}: {e}")
                return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        print(f"\n--- [ADMIN AUTH] Request path: {request.url.path} ---")
        print(f"[ADMIN AUTH] Secret key used: '{settings.SESSION_SECRET_KEY}'")
        print(f"[ADMIN AUTH] Starlette Session keys: {list(request.session.keys())}")

        session_cookie = request.cookies.get("session")
        print(f"[ADMIN AUTH] Raw 'session' cookie present: {bool(session_cookie)}")

        if session_cookie:
            try:
                # Starlette использует TimestampSigner, так как max_age по умолчанию 14 дней
                signer = TimestampSigner(settings.SESSION_SECRET_KEY)
                # Пытаемся расшифровать вручную
                decoded_bytes = signer.unsign(session_cookie, max_age=14 * 24 * 60 * 60)
                decoded_dict = json.loads(decoded_bytes.decode("utf-8"))
                print(f"[ADMIN AUTH] Manually decoded session: {decoded_dict}")
            except BadSignature as e:
                print(f"[ADMIN AUTH] BadSignature (cookie invalid or expired): {e}")
            except Exception as e:
                print(f"[ADMIN AUTH] Manual decode error: {type(e).__name__}: {e}")

        admin_user_id = request.session.get("admin_user_id")

        if not admin_user_id:
            # Fallback на JWT
            token = request.cookies.get("access_token")
            if not token:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]

            if token:
                payload = decode_access_token(token)
                if payload and "sub" in payload:
                    admin_user_id = payload["sub"]
                    print(f"[ADMIN AUTH] Fallback to JWT: found user_id {admin_user_id}")

        if not admin_user_id:
            print("[ADMIN AUTH] Failed: no admin_user_id found in session or JWT")
            return False

        async with AsyncSessionLocal() as session:
            user_repo = UserRepo(session)
            user_svc = UserService(user_repo)
            try:
                user = await user_svc.get_by_id(UUID(admin_user_id))
                if user and user.role == "admin" and user.is_active:
                    request.session.update({"admin_user_id": str(user.id)})
                    print(f"[ADMIN AUTH] Success for user {user.email}")
                    return True
                print(f"[ADMIN AUTH] Failed: user not found, inactive or not admin.")
                return False
            except Exception as e:
                print(f"[ADMIN AUTH] DB Exception: {type(e).__name__}: {e}")
                return False
