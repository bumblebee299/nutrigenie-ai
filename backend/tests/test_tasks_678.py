"""Tests for Tasks 6, 7, and 8 — food swap, label analysis, and dashboard."""

import io
import json
import pytest
from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport
from PIL import Image as PILImage

from backend.main import app
from backend.services.auth_service import create_access_token
from backend.prompts.food_swap_prompt import build_food_swap_prompt, parse_food_swap_json
from backend.prompts.label_analysis_prompt import (
    build_label_analysis_prompt,
    parse_label_analysis_json,
)
from backend.services.dashboard_service import _compute_summary, _build_charts_data
from backend.models.dashboard import DailyEntry

_TRANSPORT = ASGITransport(app=app)
_USER_ID = "tasks-678-test-uuid"
_TOKEN = create_access_token(_USER_ID)
_HEADERS = {"Authorization": f"Bearer {_TOKEN}"}

_MOCK_USER = {
    "_id": _USER_ID,
    "name": "Test User",
    "email": "t678@example.com",
    "is_active": True,
    "created_at": "2024-01-01T00:00:00+00:00",
    "updated_at": "2024-01-01T00:00:00+00:00",
}


def _make_png() -> bytes:
    buf = io.BytesIO()
    PILImage.new("RGB", (80, 80), color=(100, 150, 200)).save(buf, format="PNG")
    return buf.getvalue()


# ─── Task 6: Food Swap ───────────────────────────────────────────────────────

_MOCK_SWAP_JSON = {
    "original_food": "Pizza",
    "swaps": [
        {
            "original": "Pizza",
            "healthier_option": "Whole wheat vegetable pizza",
            "calorie_reduction": 120,
            "benefits": ["More fibre", "Less saturated fat"],
            "preparation_tip": "Use a wholemeal base and load with vegetables.",
            "explanation": "Wholemeal flour raises the fibre content significantly.",
        }
    ],
    "general_advice": "Limit processed foods in favour of whole ingredients.",
}


class TestFoodSwapPrompt:
    def test_prompt_contains_food_item(self) -> None:
        prompt = build_food_swap_prompt("Burger", [])
        assert "Burger" in prompt

    def test_prompt_includes_dietary_restrictions(self) -> None:
        prompt = build_food_swap_prompt("Burger", ["vegan", "gluten-free"])
        assert "vegan" in prompt
        assert "gluten-free" in prompt

    def test_prompt_ends_with_nutrigenie_label(self) -> None:
        prompt = build_food_swap_prompt("Ice cream", [])
        assert prompt.strip().endswith("NutriGenie:")

    def test_parse_valid_json(self) -> None:
        result = parse_food_swap_json(json.dumps(_MOCK_SWAP_JSON))
        assert result["original_food"] == "Pizza"
        assert len(result["swaps"]) == 1

    def test_parse_markdown_wrapped_json(self) -> None:
        raw = f"```json\n{json.dumps(_MOCK_SWAP_JSON)}\n```"
        result = parse_food_swap_json(raw)
        assert "swaps" in result

    def test_raises_on_empty(self) -> None:
        with pytest.raises(ValueError, match="No JSON object found"):
            parse_food_swap_json("")

    def test_raises_on_malformed(self) -> None:
        with pytest.raises(ValueError, match="Malformed JSON"):
            parse_food_swap_json("{invalid}")


class TestFoodSwapRoute:
    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.food_swap.suggest_food_swaps")
    async def test_returns_200_with_swaps(
        self, mock_swap: MagicMock, mock_user: MagicMock
    ) -> None:
        from backend.models.food_swap import FoodSwapResponse, SwapOption

        mock_user.return_value = _MOCK_USER
        mock_swap.return_value = FoodSwapResponse(
            original_food="Pizza",
            swaps=[
                SwapOption(
                    original="Pizza",
                    healthier_option="Veggie whole wheat pizza",
                    calorie_reduction=120,
                    benefits=["More fibre"],
                    preparation_tip="Use wholemeal base.",
                    explanation="Higher fibre, lower fat.",
                )
            ],
            general_advice="Eat more vegetables.",
        )

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/food-swap/",
                json={"food_item": "Pizza", "user_id": _USER_ID},
                headers=_HEADERS,
            )
        assert response.status_code == 200
        body = response.json()
        assert "swaps" in body
        assert "general_advice" in body

    @pytest.mark.asyncio
    async def test_requires_authentication(self) -> None:
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/food-swap/",
                json={"food_item": "Pizza", "user_id": _USER_ID},
            )
        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    async def test_user_id_mismatch_returns_403(self, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/food-swap/",
                json={"food_item": "Pizza", "user_id": "wrong-id"},
                headers=_HEADERS,
            )
        assert response.status_code == 403

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.food_swap.suggest_food_swaps")
    async def test_granite_failure_returns_503(
        self, mock_swap: MagicMock, mock_user: MagicMock
    ) -> None:
        mock_user.return_value = _MOCK_USER
        mock_swap.side_effect = RuntimeError("timeout")
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/food-swap/",
                json={"food_item": "Pizza", "user_id": _USER_ID},
                headers=_HEADERS,
            )
        assert response.status_code == 503


# ─── Task 7: Nutrition Label Analysis ────────────────────────────────────────

_MOCK_LABEL_JSON = {
    "product_name": "Chocolate Bar",
    "serving_size": "40g",
    "calories_per_serving": 210,
    "sugar": {"name": "Sugar", "amount": "22g", "daily_value_percent": 24.0, "assessment": "High"},
    "fat": {"name": "Total Fat", "amount": "12g", "daily_value_percent": 15.0, "assessment": "Moderate"},
    "protein": {"name": "Protein", "amount": "3g", "daily_value_percent": None, "assessment": "Low"},
    "sodium": {"name": "Sodium", "amount": "45mg", "daily_value_percent": 2.0, "assessment": "Low"},
    "additional_nutrients": [],
    "warnings": [{"category": "Sugar", "message": "High added sugar content.", "severity": "high"}],
    "overall_assessment": "This is a high-sugar, moderate-fat snack.",
    "explanation": "Limit to occasional consumption due to high sugar.",
}


class TestLabelPrompt:
    def test_prompt_contains_label_text(self) -> None:
        prompt = build_label_analysis_prompt("Sugar: 12g, Fat: 5g")
        assert "Sugar: 12g, Fat: 5g" in prompt

    def test_prompt_ends_with_nutrigenie_label(self) -> None:
        prompt = build_label_analysis_prompt("some label")
        assert prompt.strip().endswith("NutriGenie:")

    def test_parse_valid_json(self) -> None:
        result = parse_label_analysis_json(json.dumps(_MOCK_LABEL_JSON))
        assert result["calories_per_serving"] == 210

    def test_parse_markdown_wrapped(self) -> None:
        raw = f"```json\n{json.dumps(_MOCK_LABEL_JSON)}\n```"
        result = parse_label_analysis_json(raw)
        assert "sugar" in result

    def test_raises_on_empty(self) -> None:
        with pytest.raises(ValueError, match="No JSON object found"):
            parse_label_analysis_json("")


class TestLabelRoute:
    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.label_analysis.analyse_nutrition_label")
    async def test_upload_returns_200(
        self, mock_analyse: MagicMock, mock_user: MagicMock
    ) -> None:
        from backend.models.label_analysis import LabelAnalysisResponse, NutrientDetail, LabelWarning

        mock_user.return_value = _MOCK_USER
        mock_analyse.return_value = LabelAnalysisResponse(
            product_name="Test Product",
            serving_size="100g",
            calories_per_serving=150,
            sugar=NutrientDetail(name="Sugar", amount="10g", assessment="Moderate"),
            fat=NutrientDetail(name="Fat", amount="5g", assessment="Low"),
            protein=NutrientDetail(name="Protein", amount="8g", assessment="Good"),
            sodium=NutrientDetail(name="Sodium", amount="200mg", assessment="Moderate"),
            warnings=[],
            overall_assessment="Reasonably balanced.",
            explanation="A moderate snack option.",
        )

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/label-analysis/",
                headers=_HEADERS,
                data={"user_id": _USER_ID},
                files={"label_image": ("label.png", _make_png(), "image/png")},
            )
        assert response.status_code == 200
        body = response.json()
        assert "sugar" in body
        assert "warnings" in body
        assert "explanation" in body

    @pytest.mark.asyncio
    async def test_requires_authentication(self) -> None:
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/label-analysis/",
                data={"user_id": _USER_ID},
                files={"label_image": ("l.png", _make_png(), "image/png")},
            )
        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    async def test_unsupported_type_returns_415(self, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/label-analysis/",
                headers=_HEADERS,
                data={"user_id": _USER_ID},
                files={"label_image": ("doc.pdf", b"pdf", "application/pdf")},
            )
        assert response.status_code == 415


# ─── Task 8: Dashboard ───────────────────────────────────────────────────────

_DAILY_ENTRIES = [
    DailyEntry(date=date(2024, 1, 1), calories_consumed=1800, protein_g=90, water_ml=2500, weight_kg=72.0),
    DailyEntry(date=date(2024, 1, 2), calories_consumed=2000, protein_g=110, water_ml=2200, weight_kg=71.8),
    DailyEntry(date=date(2024, 1, 3), calories_consumed=1700, protein_g=95, water_ml=3000, weight_kg=71.6),
]


class TestDashboardService:
    def test_compute_summary_averages(self) -> None:
        summary = _compute_summary(_DAILY_ENTRIES)
        assert summary.avg_calories == pytest.approx(1833.3, rel=0.01)
        assert summary.avg_protein_g == pytest.approx(98.3, rel=0.01)

    def test_weight_change_is_computed(self) -> None:
        summary = _compute_summary(_DAILY_ENTRIES)
        assert summary.weight_change_kg == pytest.approx(-0.4, rel=0.01)

    def test_empty_entries_returns_zeroes(self) -> None:
        summary = _compute_summary([])
        assert summary.avg_calories == 0.0
        assert summary.goal_adherence_percent == 0.0

    def test_single_entry_no_weight_change(self) -> None:
        entries = [DailyEntry(date=date(2024, 1, 1), calories_consumed=1800, protein_g=80, water_ml=2000, weight_kg=70.0)]
        summary = _compute_summary(entries)
        assert summary.weight_change_kg is None

    def test_charts_data_has_all_series(self) -> None:
        charts = _build_charts_data(_DAILY_ENTRIES)
        assert "calories" in charts
        assert "protein" in charts
        assert "water" in charts
        assert "weight" in charts
        assert len(charts["calories"]) == 3

    def test_charts_water_converted_to_litres(self) -> None:
        charts = _build_charts_data(_DAILY_ENTRIES)
        first = charts["water"][0]["value"]
        assert first == pytest.approx(2.5, rel=0.01)


class TestDashboardRoute:
    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.dashboard.get_weekly_dashboard")
    async def test_returns_dashboard_data(
        self, mock_dash: MagicMock, mock_user: MagicMock
    ) -> None:
        from backend.models.dashboard import DashboardResponse, WeeklySummary

        mock_user.return_value = _MOCK_USER
        mock_dash.return_value = DashboardResponse(
            user_id=_USER_ID,
            week_start=date(2024, 1, 1),
            week_end=date(2024, 1, 7),
            daily_entries=_DAILY_ENTRIES,
            summary=WeeklySummary(
                avg_calories=1833.3, avg_protein_g=98.3,
                avg_water_ml=2566.7, weight_change_kg=-0.4,
                goal_adherence_percent=42.9,
            ),
            charts_data=_build_charts_data(_DAILY_ENTRIES),
        )

        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.get(
                f"/dashboard/{_USER_ID}?week_start=2024-01-01",
                headers=_HEADERS,
            )
        assert response.status_code == 200
        body = response.json()
        assert "daily_entries" in body
        assert "summary" in body
        assert "charts_data" in body

    @pytest.mark.asyncio
    async def test_requires_authentication(self) -> None:
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.get(
                f"/dashboard/{_USER_ID}?week_start=2024-01-01"
            )
        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    async def test_user_id_mismatch_returns_403(self, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.get(
                f"/dashboard/wrong-user-id?week_start=2024-01-01",
                headers=_HEADERS,
            )
        assert response.status_code == 403

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    async def test_missing_week_start_returns_422(self, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.get(
                f"/dashboard/{_USER_ID}",
                headers=_HEADERS,
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.dashboard.log_meal")
    async def test_log_meal_route(self, mock_log: MagicMock, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        mock_log.return_value = {"_id": "test-doc"}
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                f"/dashboard/{_USER_ID}/meal",
                json={
                    "date": "2024-01-01",
                    "type": "breakfast",
                    "name": "Oatmeal",
                    "calories": 250,
                    "protein_g": 10.0,
                },
                headers=_HEADERS,
            )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        mock_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.dashboard.log_water")
    async def test_log_water_route(self, mock_log: MagicMock, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        mock_log.return_value = {"_id": "test-doc"}
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                f"/dashboard/{_USER_ID}/water",
                json={
                    "date": "2024-01-01",
                    "amount_ml": 250,
                },
                headers=_HEADERS,
            )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        mock_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.dashboard.log_weight")
    async def test_log_weight_route(self, mock_log: MagicMock, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        mock_log.return_value = {"_id": "test-doc"}
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                f"/dashboard/{_USER_ID}/weight",
                json={
                    "date": "2024-01-01",
                    "weight_kg": 70.5,
                },
                headers=_HEADERS,
            )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        mock_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.dashboard.log_feedback")
    async def test_log_feedback_route(self, mock_log: MagicMock, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        mock_log.return_value = {"_id": "test-doc"}
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                f"/dashboard/{_USER_ID}/feedback",
                json={
                    "date": "2024-01-01",
                    "rating": 5,
                    "comment": "Feeling great!",
                },
                headers=_HEADERS,
            )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        mock_log.assert_called_once()

