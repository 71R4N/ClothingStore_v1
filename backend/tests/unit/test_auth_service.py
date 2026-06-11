import pytest
from unittest.mock import AsyncMock, MagicMock
from app.auth.services import AuthService
from app.auth.schemas import RegisterRequest
from app.auth.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    CaptchaRequiredError,
)
from app.users.schemas import UserCreate


class TestAuthServiceRegister:

    @pytest.mark.asyncio
    async def test_register_success(self):
        user_service = MagicMock()
        user_service.get_by_email = AsyncMock(return_value=None)
        user_service.create_user = AsyncMock(return_value=1)
        service = AuthService(user_service)
        data = RegisterRequest(
            email="new@example.com",
            password="StrongPass1!",
            first_name="New",
            last_name="User",
        )
        user_id = await service.register(data)
        assert user_id == 1
        user_service.create_user.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_register_email_exists(self):
        user_service = MagicMock()
        user_service.get_by_email = AsyncMock(return_value=MagicMock())
        service = AuthService(user_service)
        data = RegisterRequest(
            email="exists@example.com",
            password="StrongPass1!",
            first_name="A",
            last_name="B",
        )
        with pytest.raises(EmailAlreadyExistsError):
            await service.register(data)


class TestAuthServiceAuthenticate:

    @pytest.mark.asyncio
    async def test_authenticate_wrong_credentials(self):
        user_service = MagicMock()
        user_service.get_by_email = AsyncMock(return_value=None)
        service = AuthService(user_service)
        with pytest.raises(InvalidCredentialsError):
            await service.authenticate(
                email="bad@example.com",
                password="wrong",
                client_ip="127.0.0.1",
            )
