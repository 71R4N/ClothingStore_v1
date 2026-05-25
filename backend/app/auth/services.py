from datetime import timedelta
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.users.services import UserService
from app.auth.exceptions import InvalidCredentialsError, EmailAlreadyExistsError
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

    async def authenticate(self, email: str, password: str) -> str:
        user = await self.user_service.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        token = create_access_token(data={"sub": str(user.id)})
        return token
