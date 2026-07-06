"""Unit and integration tests for food image analysis."""

import io
import json
import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport
from PIL import Image as PILImage

from backend.main import app
from backend.services.auth_service import create_access_token
from backend.prompts.image_analysis_prompt import (
    build_image_analysis_prompt,
    parse_image_analysis_json,
)
from backend.services.image_analysis_service import validate_image, resize_image

_TRANSPORT = ASGITransport(app=app)
_USER_ID = "image-analysis-test-uuid"
_TOKEN = create_access_token(_USER_ID)
_HEADERS = {"Authorization": f"Bearer {_TOKEN}"}

_MOCK_USER = {
    "_id": _USER_ID,
    "name": "Image Tester",
    "email": "img@example.com",
    "is_active": True,
    "created_at": "2024-01-01T00:00:00+00:00",
    "updated_at": "2024-01-01T00:00:00+00:00",
}

_MOCK_ANALYSIS_JSON = {
    "detected_foods": [
        {"name": "Pizza slice", "confidence": 0.95, "estimated_calories": 285, "portion_size": "1 slice"},
        {"name": "Cola", "confidence": 0.88, "estimated_calories": 140, "portion_size": "330ml can"},
    ],
    "total_estimated_calories": 425,
    "healthier_alternatives": [
        {
            "original": "Pizza slice",
            "alternative": "Whole wheat vegetable pizza",
            "reason": "Lower refined carbs, more fibre and micronutrients.",
            "calorie_difference": 80,
        }
    ],
    "nutritional_notes": "High sodium and refined carbohydrate meal.",
    "explanation": "This meal is calorie-dense. Swapping to whole wheat pizza would improve nutritional quality.",
}


def _make_png_bytes(width: int = 100, height: int = 100) -> bytes:
    """Create a minimal valid PNG image in memory."""
    img = PILImage.new("RGB", (width, height), color=(255, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestImagePrompt:
    def test_prompt_contains_description(self) -> None:
        prompt = build_image_analysis_prompt("A bowl of oatmeal with berries.")
        assert "A bowl of oatmeal with berries." in prompt

    def test_prompt_ends_with_nutrigenie_label(self) -> None:
        prompt = build_image_analysis_prompt("some food")
        assert prompt.strip().endswith("NutriGenie:")

    def test_parse_valid_json(self) -> None:
        result = parse_image_analysis_json(json.dumps(_MOCK_ANALYSIS_JSON))
        assert result["total_estimated_calories"] == 425

    def test_parse_json_in_markdown_fence(self) -> None:
        raw = f"```json\n{json.dumps(_MOCK_ANALYSIS_JSON)}\n```"
        result = parse_image_analysis_json(raw)
        assert len(result["detected_foods"]) == 2

    def test_raises_on_empty_output(self) -> None:
        with pytest.raises(ValueError, match="No JSON object found"):
            parse_image_analysis_json("")

    def test_raises_on_malformed_json(self) -> None:
        with pytest.raises(ValueError, match="Malformed JSON"):
            parse_image_analysis_json("{invalid}")


class TestImageValidation:
    def test_valid_jpeg_passes(self) -> None:
        validate_image(b"data", "image/jpeg")  # no exception

    def test_valid_png_passes(self) -> None:
        validate_image(b"data", "image/png")

    def test_unsupported_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported file type"):
            validate_image(b"data", "application/pdf")


class TestResizeImage:
    def test_small_image_unchanged(self) -> None:
        data = _make_png_bytes(100, 100)
        result = resize_image(data)
        assert result == data

    def test_large_image_is_resized(self) -> None:
        data = _make_png_bytes(2000, 2000)
        result = resize_image(data)
        img = PILImage.open(io.BytesIO(result))
        assert img.width <= 1024
        assert img.height <= 1024


class TestImageAnalysisRoute:
    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.image_analysis.analyse_food_image")
    async def test_upload_returns_200(
        self, mock_analyse: MagicMock, mock_user: MagicMock
    ) -> None:
        from backend.models.image_analysis import ImageAnalysisResponse, FoodItem, HealthierAlternative

        mock_user.return_value = _MOCK_USER
        mock_analyse.return_value = ImageAnalysisResponse(
            detected_foods=[
                FoodItem(name="Pizza", confidence=0.95, estimated_calories=285, portion_size="1 slice")
            ],
            total_estimated_calories=285,
            healthier_alternatives=[
                HealthierAlternative(
                    original="Pizza", alternative="Veggie pizza",
                    reason="More fibre", calorie_difference=80,
                )
            ],
            nutritional_notes="High sodium.",
            explanation="Swap for a healthier option.",
            image_url="https://cos.example.com/img.jpg",
        )

        image_bytes = _make_png_bytes()
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/image-analysis/",
                headers=_HEADERS,
                data={"user_id": _USER_ID},
                files={"image": ("test.png", image_bytes, "image/png")},
            )

        assert response.status_code == 200
        body = response.json()
        assert "detected_foods" in body
        assert "total_estimated_calories" in body
        assert "healthier_alternatives" in body
        assert "explanation" in body

    @pytest.mark.asyncio
    async def test_upload_requires_authentication(self) -> None:
        image_bytes = _make_png_bytes()
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/image-analysis/",
                data={"user_id": _USER_ID},
                files={"image": ("test.png", image_bytes, "image/png")},
            )
        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    async def test_unsupported_file_type_returns_415(self, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/image-analysis/",
                headers=_HEADERS,
                data={"user_id": _USER_ID},
                files={"image": ("doc.pdf", b"pdfcontent", "application/pdf")},
            )
        assert response.status_code == 415

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    async def test_user_id_mismatch_returns_403(self, mock_user: MagicMock) -> None:
        mock_user.return_value = _MOCK_USER
        image_bytes = _make_png_bytes()
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/image-analysis/",
                headers=_HEADERS,
                data={"user_id": "wrong-user-id"},
                files={"image": ("test.png", image_bytes, "image/png")},
            )
        assert response.status_code == 403

    @pytest.mark.asyncio
    @patch("backend.api.dependencies.get_user_by_id")
    @patch("backend.routes.image_analysis.analyse_food_image")
    async def test_granite_failure_returns_503(
        self, mock_analyse: MagicMock, mock_user: MagicMock
    ) -> None:
        mock_user.return_value = _MOCK_USER
        mock_analyse.side_effect = RuntimeError("Granite timeout")
        image_bytes = _make_png_bytes()
        async with AsyncClient(transport=_TRANSPORT, base_url="http://test") as client:
            response = await client.post(
                "/image-analysis/",
                headers=_HEADERS,
                data={"user_id": _USER_ID},
                files={"image": ("test.png", image_bytes, "image/png")},
            )
        assert response.status_code == 503
