"""Unit tests for the meal plan service layer."""

import json
import pytest
from unittest.mock import MagicMock, patch

from backend.services.meal_plan_service import calculate_tdee
from backend.prompts.meal_plan_prompt import build_meal_plan_prompt, parse_meal_plan_json


class TestCalculateTDEE:
    def test_male_sedentary_maintenance(self) -> None:
        """Basic male sedentary TDEE — no goal adjustment."""
        kcal = calculate_tdee(
            age=30, height_cm=175, weight_kg=75,
            gender="male", lifestyle="sedentary", goal="maintenance",
        )
        # Mifflin: 10*75 + 6.25*175 - 5*30 + 5 = 750+1093.75-150+5 = 1698.75 → ×1.2 = 2038.5
        assert 2000 <= kcal <= 2100

    def test_female_active_weight_loss(self) -> None:
        """Female moderately active, weight loss subtracts 500 kcal from TDEE."""
        kcal = calculate_tdee(
            age=25, height_cm=165, weight_kg=65,
            gender="female", lifestyle="moderately_active", goal="weight_loss",
        )
        assert kcal > 1200  # floor enforced

    def test_calorie_floor_is_1200(self) -> None:
        """Extremely low result must be clamped to 1200 kcal."""
        kcal = calculate_tdee(
            age=80, height_cm=140, weight_kg=35,
            gender="female", lifestyle="sedentary", goal="weight_loss",
        )
        assert kcal >= 1200

    def test_weight_gain_adds_calories(self) -> None:
        """Weight gain goal should produce a higher target than maintenance."""
        maintenance = calculate_tdee(30, 175, 70, "male", "sedentary", "maintenance")
        gain = calculate_tdee(30, 175, 70, "male", "sedentary", "weight_gain")
        assert gain > maintenance

    def test_muscle_gain_adds_calories(self) -> None:
        maintenance = calculate_tdee(25, 180, 80, "male", "lightly_active", "maintenance")
        muscle = calculate_tdee(25, 180, 80, "male", "lightly_active", "muscle_gain")
        assert muscle > maintenance


class TestMealPlanPrompt:
    def test_prompt_contains_user_profile_data(self) -> None:
        prompt = build_meal_plan_prompt(
            age=28, height_cm=170, weight_kg=72, gender="male",
            goal="weight_loss", diseases=["diabetes"], allergies=["nuts"],
            cuisine_preference=["Mediterranean"], budget_usd_per_day=15.0,
            lifestyle="moderately_active", target_calories=1800,
        )
        assert "28" in prompt
        assert "170" in prompt
        assert "diabetes" in prompt
        assert "nuts" in prompt
        assert "Mediterranean" in prompt
        assert "1800" in prompt

    def test_prompt_ends_with_nutrigenie_label(self) -> None:
        prompt = build_meal_plan_prompt(
            age=30, height_cm=175, weight_kg=75, gender="male",
            goal="maintenance", diseases=[], allergies=[],
            cuisine_preference=[], budget_usd_per_day=None,
            lifestyle="sedentary", target_calories=2000,
        )
        assert prompt.strip().endswith("NutriGenie:")

    def test_no_allergies_shows_none(self) -> None:
        prompt = build_meal_plan_prompt(
            age=30, height_cm=175, weight_kg=75, gender="male",
            goal="maintenance", diseases=[], allergies=[],
            cuisine_preference=[], budget_usd_per_day=None,
            lifestyle="sedentary", target_calories=2000,
        )
        assert "none" in prompt

    def test_no_budget_shows_no_constraint(self) -> None:
        prompt = build_meal_plan_prompt(
            age=30, height_cm=175, weight_kg=75, gender="male",
            goal="maintenance", diseases=[], allergies=[],
            cuisine_preference=[], budget_usd_per_day=None,
            lifestyle="sedentary", target_calories=2000,
        )
        assert "no constraint" in prompt


class TestParseMealPlanJson:
    _VALID = {
        "breakfast": {
            "name": "Oatmeal", "ingredients": ["oats", "milk"],
            "calories": 350, "protein_g": 12, "carbs_g": 55, "fat_g": 7,
            "preparation_time_minutes": 10,
            "instructions": "Cook oats.", "explanation": "High fibre.",
        },
        "lunch": {
            "name": "Salad", "ingredients": ["lettuce"],
            "calories": 400, "protein_g": 20, "carbs_g": 30, "fat_g": 10,
            "preparation_time_minutes": 5,
            "instructions": "Toss.", "explanation": "Light.",
        },
        "dinner": {
            "name": "Chicken", "ingredients": ["chicken"],
            "calories": 500, "protein_g": 45, "carbs_g": 20, "fat_g": 15,
            "preparation_time_minutes": 30,
            "instructions": "Grill.", "explanation": "Protein rich.",
        },
        "snacks": [],
        "nutrition_summary": {
            "total_calories": 1250, "protein_g": 77, "carbs_g": 105,
            "fat_g": 32, "fiber_g": 18, "water_ml": 2500,
        },
        "explanation": "Balanced plan.",
    }

    def test_parses_plain_json(self) -> None:
        result = parse_meal_plan_json(json.dumps(self._VALID))
        assert result["breakfast"]["name"] == "Oatmeal"

    def test_parses_json_wrapped_in_markdown_fence(self) -> None:
        raw = f"```json\n{json.dumps(self._VALID)}\n```"
        result = parse_meal_plan_json(raw)
        assert "breakfast" in result

    def test_parses_json_with_leading_prose(self) -> None:
        raw = f"Here is your meal plan:\n{json.dumps(self._VALID)}"
        result = parse_meal_plan_json(raw)
        assert "lunch" in result

    def test_raises_on_empty_string(self) -> None:
        with pytest.raises(ValueError, match="No JSON object found"):
            parse_meal_plan_json("")

    def test_raises_on_malformed_json(self) -> None:
        with pytest.raises(ValueError, match="Malformed JSON"):
            parse_meal_plan_json("{not valid json}")
