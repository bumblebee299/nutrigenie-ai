"""Integration tests for the POST /meal-plan route."""

import json
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.services.auth_service import create_access_token

_TRANSPORT = ASGITransport(app=app)
_USER_ID = "meal-plan-test-user-uuid"
_TOKEN = create_access_token(_USER_ID)
_HEADERS = {"Authorization": f"Bearer {_TOKEN}"}

_MOCK_USER = {
    "_id": _USER_ID,
    "name": "Meal Tester",
    "email": "meal@example.com",
    "is_active": True,
    "created_at": "2024-01-01T00:00:00+00:00",
    "updated_at": "2024-01-01T00:00:00+00:00",
}

_VALID_PAYLOAD = {
    "user_id": _USER_ID,
    "age": 28,
    "height_cm": 170.0,
    "weight_kg": 72.0,
    "gender": "male",
    "goal": "weight_loss",
    "diseases": [],
    "allergies": ["nuts"],
    "cuisine_preference": ["Mediterranean"],
    "lifestyle": "moderately_active",
}

_MOCK_MEAL = {
    "name": "Grilled Chicken Salad",
    "ingredients": ["chicken", "lettuce", "tomato"],
    "calories": 450,
    "protein_g": 40.0,
    "carbs_g": 20.0,
    "fat_g": 15.0,
    "preparation_time_minutes": 20,
    "instructions": "Grill chicken and toss with salad.",
    "explanation": "High protein, low carb meal ideal for weight loss.",
}

_MOCK_PLAN_RESPONSE = {
    "user_id": _USER_ID,
    "breakfast": _MOCK_MEAL,
    "lunch": _MOCK_MEAL,
    "dinner": _MOCK_MEAL,
    "snacks": [],
    "nutrition_summary": {
        "total_calories": 1350,
        "protein_g": 120.0,
        "carbs_g": 60.0,
        "fat_g": 45.0,
        "fiber_g": 20.0,
        "water_ml": 2500,
    },
    "explanation": "This plan targets a 500 kcal deficit for steady weight loss.",
}


class TestMealPlanRoute:
    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.meal_plan.generate_meal_plan")
    async def test_create_meal_plan_returns_201(
        self, mock_generate: MagicMock, mock_user: MagicMock
    ) -> None:
        from backend.models.meal_plan import MealPlanResponse
        mock_user.return_value = _MOCK_USER
        mock_generate.return_value = MealPlanResponse(**_MOCK_PLAN_RESPONSE)

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post("/meal-plan/", json=_VALID_PAYLOAD, headers=_HEADERS)

        assert response.status_code == 201
        body = response.json()
        assert "breakfast" in body
        assert "nutrition_summary" in body
        assert "explanation" in body

    @pytest.mark.asyncio
    async def test_meal_plan_requires_authentication(self) -> None:
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post("/meal-plan/", json=_VALID_PAYLOAD)
        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    async def test_meal_plan_user_id_mismatch_returns_403(
        self, mock_user: MagicMock
    ) -> None:
        mock_user.return_value = _MOCK_USER
        payload = {**_VALID_PAYLOAD, "user_id": "wrong-user-id"}

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post("/meal-plan/", json=payload, headers=_HEADERS)
        assert response.status_code == 403

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.meal_plan.generate_meal_plan")
    async def test_granite_failure_returns_503(
        self, mock_generate: MagicMock, mock_user: MagicMock
    ) -> None:
        mock_user.return_value = _MOCK_USER
        mock_generate.side_effect = RuntimeError("Granite timeout")

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post("/meal-plan/", json=_VALID_PAYLOAD, headers=_HEADERS)
        assert response.status_code == 503

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.meal_plan.generate_meal_plan")
    async def test_json_parse_failure_returns_502(
        self, mock_generate: MagicMock, mock_user: MagicMock
    ) -> None:
        mock_user.return_value = _MOCK_USER
        mock_generate.side_effect = ValueError("No JSON object found")

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post("/meal-plan/", json=_VALID_PAYLOAD, headers=_HEADERS)
        assert response.status_code == 502

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    async def test_invalid_age_returns_422(self, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        payload = {**_VALID_PAYLOAD, "age": 0}
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post("/meal-plan/", json=payload, headers=_HEADERS)
        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    async def test_invalid_gender_returns_422(self, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        payload = {**_VALID_PAYLOAD, "gender": "robot"}
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post("/meal-plan/", json=payload, headers=_HEADERS)
        assert response.status_code == 422
