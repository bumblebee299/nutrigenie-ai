"""Integration tests for the /auth routes using AsyncClient."""

import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport

from backend.main import app

_APP_TRANSPORT = ASGITransport(app=app)


_MOCK_USER_DOC = {
    "_id": "test-user-uuid",
    "name": "Test User",
    "email": "test@example.com",
    "hashed_password": "$2b$12$placeholder_bcrypt_hash",
    "is_active": True,
    "created_at": "2024-01-01T00:00:00+00:00",
    "updated_at": "2024-01-01T00:00:00+00:00",
}


class TestRegisterRoute:
    @pytest.mark.asyncio
    @patch("backend.routes.auth.create_user")
    async def test_register_returns_201(self, mock_create: MagicMock) -> None:
        from datetime import datetime, timezone
        from backend.models.auth import UserPublic

        mock_create.return_value = UserPublic(
            id="new-uuid",
            name="Jane Doe",
            email="jane@example.com",
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )

        async with AsyncClient(transport=_APP_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={"name": "Jane Doe", "email": "jane@example.com", "password": "password123"},
            )
        assert response.status_code == 201
        assert response.json()["email"] == "jane@example.com"

    @pytest.mark.asyncio
    @patch("backend.routes.auth.create_user")
    async def test_register_conflict_returns_409(self, mock_create: MagicMock) -> None:
        mock_create.side_effect = ValueError("An account with this email address already exists.")

        async with AsyncClient(transport=_APP_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={"name": "Dup User", "email": "dup@example.com", "password": "password123"},
            )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_short_password_returns_422(self) -> None:
        async with AsyncClient(transport=_APP_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={"name": "Bad User", "email": "bad@example.com", "password": "short"},
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email_returns_422(self) -> None:
        async with AsyncClient(transport=_APP_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={"name": "Bad Email", "email": "not-an-email", "password": "password123"},
            )
        assert response.status_code == 422


class TestLoginRoute:
    @pytest.mark.asyncio
    @patch("backend.routes.auth.authenticate_user")
    async def test_login_success_returns_tokens(self, mock_auth: MagicMock) -> None:
        mock_auth.return_value = _MOCK_USER_DOC

        async with AsyncClient(transport=_APP_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                data={"username": "test@example.com", "password": "password123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    @patch("backend.routes.auth.authenticate_user")
    async def test_login_wrong_credentials_returns_401(self, mock_auth: MagicMock) -> None:
        mock_auth.return_value = None

        async with AsyncClient(transport=_APP_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                data={"username": "test@example.com", "password": "wrongpassword"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        assert response.status_code == 401


class TestRefreshRoute:
    @pytest.mark.asyncio
    async def test_invalid_refresh_token_returns_401(self) -> None:
        async with AsyncClient(transport=_APP_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/auth/refresh", json={"refresh_token": "invalid.token.here"}
            )
        assert response.status_code == 401
