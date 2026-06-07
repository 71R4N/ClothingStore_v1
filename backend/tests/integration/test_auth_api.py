import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestAuthAPI:
    """Интеграционные тесты эндпоинтов аутентификации."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """POST /auth/register — успешная регистрация возвращает 201 и токен."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "StrongPass1!",
            "first_name": "Ivan",
            "last_name": "Ivanov",
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Проверяем наличие refresh-куки
        cookies = response.cookies
        assert "refresh_token" in cookies

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user
    ):
        """POST /auth/register — 409 при повторной регистрации."""
        response = await client.post("/api/v1/auth/register", json={
            "email": test_user.email,
            "password": "StrongPass1!",
            "first_name": "Dup",
            "last_name": "User",
        })
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """POST /auth/register — 422 при слабом пароле."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "weak@example.com",
            "password": "123",  # слишком короткий, нет спецсимволов
            "first_name": "A",
            "last_name": "B",
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_success(
        self, client: AsyncClient, test_user
    ):
        """POST /auth/login — успешный вход возвращает токен."""
        # Получаем CSRF-токен
        csrf_resp = await client.get("/api/v1/auth/csrf")
        csrf_token = csrf_resp.cookies.get("csrf_token")

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
            },
            headers={"X-CSRF-Token": csrf_token},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, client: AsyncClient, test_user
    ):
        """POST /auth/login — 401 при неверном пароле."""
        csrf_resp = await client.get("/api/v1/auth/csrf")
        csrf_token = csrf_resp.cookies.get("csrf_token")

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPass1!",
            },
            headers={"X-CSRF-Token": csrf_token},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_route_without_token(self, client: AsyncClient):
        """GET /users/me — 401 без токена авторизации."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_route_with_token(
        self, client: AsyncClient, test_user, auth_headers
    ):
        """GET /users/me — 200 с валидным токеном."""
        response = await client.get(
            "/api/v1/users/me", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
