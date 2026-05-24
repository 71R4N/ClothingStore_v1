from backend.app.users.services import UserService
from backend.app.core.security import create_access_token, create_refresh_token

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def authenticate_user(self, email: str, password: str):
        return await self.user_service.authenticate(email, password)

    def create_tokens(self, user_id: int, email: str) -> dict:
        access_token = create_access_token(data={"sub": str(user_id), "email": email})
        refresh_token = create_refresh_token(data={"sub": str(user_id), "email": email})
        return {"access_token": access_token, "refresh_token": refresh_token}
