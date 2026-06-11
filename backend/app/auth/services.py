from app.core.redis_client import redis_client
import httpx
from app.core.security import verify_password
from app.core.config import settings
from app.users.services import UserService
from app.auth.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    CaptchaRequiredError,
    InvalidCaptchaError
)
from app.auth.schemas import RegisterRequest
from app.users.models import User


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def register(self, data: RegisterRequest) -> int:
        existing = await self.user_service.get_by_email(data.email)
        if existing:
            raise EmailAlreadyExistsError()
        from app.users.schemas import UserCreate
        user_data = UserCreate(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone
        )
        user_id = await self.user_service.create_user(user_data)
        return user_id

    async def authenticate(
            self,
            email: str,
            password: str,
            captcha_response: str | None = None,
            client_ip: str | None = None
    ) -> User:
        attempts_key = f"login_attempts:{email}:{client_ip}"
        attempts_str = await redis_client.get(attempts_key)
        attempts = int(attempts_str) if attempts_str else 0
        if attempts >= 3:
            if not captcha_response:
                raise CaptchaRequiredError()
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://www.google.com/recaptcha/api/siteverify",
                        data={"secret": settings.RECAPTCHA_SECRET_KEY,
                            "response": captcha_response,
                            "remoteip": client_ip})
                    result = resp.json()
                    if not result.get("success") or result.get("score", 1.0) < 0.5:
                        raise InvalidCaptchaError()
            except httpx.HTTPError as e:
                raise InvalidCaptchaError()
        user = await self.user_service.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            new_attempts = attempts + 1
            await redis_client.setex(attempts_key, 60, str(new_attempts))
            raise InvalidCredentialsError()
        await redis_client.delete(attempts_key)

        return user