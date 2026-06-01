from app.core.redis_client import redis_client
import httpx
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.users.services import UserService
from app.auth.exceptions import InvalidCredentialsError, EmailAlreadyExistsError, CaptchaRequiredError, InvalidCaptchaError
from app.auth.schemas import RegisterRequest

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def register(self, data: RegisterRequest) -> int:
        # проверим, нет ли уже пользователя с таким email
        existing = await self.user_service.get_by_email(data.email)
        if existing:
            raise EmailAlreadyExistsError()
        hashed_pw = hash_password(data.password)
        # используем схему создания пользователя (users.schemas.UserCreate)
        from app.users.schemas import UserCreate
        user_data = UserCreate(
            email=data.email,
            password_hash=hashed_pw,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone
        )
        user_id = await self.user_service.create_user(user_data)
        return user_id

    async def authenticate(self, email: str, password: str, captcha_response: str | None = None, client_ip: str = None) -> str:
        # Проверяем количество неудачных попыток
        attempts_key = f"login_attempts:{email}:{client_ip}"
        attempts = await redis_client.get(attempts_key)
        attempts = int(attempts) if attempts else 0

        # Если попыток больше 3 — проверяем капчу
        if attempts >= 3:
            if not captcha_response:
                raise CaptchaRequiredError()
            # Верифицируем капчу с Google
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={
                        "secret": settings.RECAPTCHA_SECRET_KEY,
                        "response": captcha_response,
                        "remoteip": client_ip
                    }
                )
                result = resp.json()
                if not result.get("success") or result.get("score", 0) < 0.5:
                    raise InvalidCaptchaError()

        # Основная логика аутентификации
        user = await self.user_service.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            # Увеличиваем счётчик неудачных попыток
            new_attempts = attempts + 1
            await redis_client.setex(attempts_key, 3600, new_attempts)  # Храним 1 час
            raise InvalidCredentialsError()

        # При успешном входе сбрасываем счётчик
        await redis_client.delete(attempts_key)
        token = create_access_token(data={"sub": str(user.id)})
        return token
