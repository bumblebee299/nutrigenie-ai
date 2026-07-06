"""Integration tests for the /chat routes."""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.services.auth_service import create_access_token

_TRANSPORT = ASGITransport(app=app)
_USER_ID = "chat-test-user-uuid"
_ACCESS_TOKEN = create_access_token(_USER_ID)
_AUTH_HEADERS = {"Authorization": f"Bearer {_ACCESS_TOKEN}"}

_MOCK_USER_DOC = {
    "_id": _USER_ID,
    "name": "Chat Tester",
    "email": "chat@example.com",
    "is_active": True,
    "created_at": "2024-01-01T00:00:00+00:00",
    "updated_at": "2024-01-01T00:00:00+00:00",
}

_MOCK_CHAT_RESPONSE = {
    "reply": "You should aim for 2000–2500 kcal per day depending on your activity.",
    "explanation": "Caloric needs vary based on basal metabolic rate and activity level.",
    "sources": [],
    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
}


class TestChatRoute:
    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.chat.answer_nutrition_question")
    async def test_chat_returns_200_with_reply(
        self,
        mock_answer: MagicMock,
        mock_get_user: MagicMock,
    ) -> None:
        from backend.models.chat import ChatResponse

        mock_get_user.return_value = _MOCK_USER_DOC
        mock_answer.return_value = ChatResponse(**_MOCK_CHAT_RESPONSE)

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/chat/",
                json={"message": "How many calories do I need?", "user_id": _USER_ID},
                headers=_AUTH_HEADERS,
            )

        assert response.status_code == 200
        body = response.json()
        assert "reply" in body
        assert "explanation" in body
        assert "timestamp" in body

    @pytest.mark.asyncio
    async def test_chat_requires_authentication(self) -> None:
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/chat/",
                json={"message": "What is protein?", "user_id": _USER_ID},
            )
        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.chat.answer_nutrition_question")
    async def test_chat_user_id_mismatch_returns_403(
        self,
        mock_answer: MagicMock,
        mock_get_user: MagicMock,
    ) -> None:
        mock_get_user.return_value = _MOCK_USER_DOC

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/chat/",
                json={"message": "test", "user_id": "different-user-uuid"},
                headers=_AUTH_HEADERS,
            )
        assert response.status_code == 403

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.chat.answer_nutrition_question")
    async def test_chat_granite_failure_returns_503(
        self,
        mock_answer: MagicMock,
        mock_get_user: MagicMock,
    ) -> None:
        mock_get_user.return_value = _MOCK_USER_DOC
        mock_answer.side_effect = RuntimeError("Granite inference error: timeout")

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/chat/",
                json={"message": "test", "user_id": _USER_ID},
                headers=_AUTH_HEADERS,
            )
        assert response.status_code == 503

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.chat.store_feedback")
    async def test_feedback_returns_204(
        self,
        mock_store: MagicMock,
        mock_get_user: MagicMock,
    ) -> None:
        mock_get_user.return_value = _MOCK_USER_DOC
        mock_store.return_value = None

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/chat/feedback",
                json={
                    "message_id": "some-message-id",
                    "helpful": True,
                    "user_id": _USER_ID,
                },
                headers=_AUTH_HEADERS,
            )
        assert response.status_code == 204
