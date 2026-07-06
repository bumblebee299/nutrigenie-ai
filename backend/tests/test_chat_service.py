"""Unit tests for prompt building and the Granite service wrapper."""

import pytest
from unittest.mock import MagicMock, patch

from backend.prompts.nutrition_prompt import build_chat_prompt, extract_explanation


class TestBuildChatPrompt:
    def test_prompt_contains_user_message(self) -> None:
        prompt = build_chat_prompt("What is vitamin C?", [])
        assert "What is vitamin C?" in prompt

    def test_prompt_contains_system_context(self) -> None:
        prompt = build_chat_prompt("hello", [])
        assert "NutriGenie" in prompt

    def test_prompt_ends_with_nutrigenie_label(self) -> None:
        prompt = build_chat_prompt("hello", [])
        assert prompt.strip().endswith("NutriGenie:")

    def test_history_is_included_in_prompt(self) -> None:
        history = [
            {"role": "user", "content": "How many calories in an apple?"},
            {"role": "assistant", "content": "About 95 calories."},
        ]
        prompt = build_chat_prompt("What about a banana?", history)
        assert "How many calories in an apple?" in prompt
        assert "About 95 calories." in prompt

    def test_history_is_capped_at_ten_turns(self) -> None:
        history = [{"role": "user", "content": f"msg {i}"} for i in range(20)]
        prompt = build_chat_prompt("final", history)
        # Only the last 10 should appear
        assert "msg 19" in prompt
        assert "msg 0" not in prompt

    def test_empty_history_produces_valid_prompt(self) -> None:
        prompt = build_chat_prompt("Tell me about protein.", [])
        assert "User: Tell me about protein." in prompt


class TestExtractExplanation:
    def test_extracts_nutritional_explanation_section(self) -> None:
        response = (
            "You should eat more fibre.\n"
            "Nutritional explanation: Fibre supports gut microbiome diversity.\n"
            "Practical tip: Add oats to breakfast."
        )
        explanation = extract_explanation(response)
        assert "Fibre supports gut microbiome diversity" in explanation

    def test_falls_back_gracefully_when_section_missing(self) -> None:
        explanation = extract_explanation("Just eat more vegetables.")
        assert len(explanation) > 0

    def test_explanation_marker_case_insensitive(self) -> None:
        response = "EXPLANATION: Protein is essential for muscle repair."
        explanation = extract_explanation(response)
        assert "Protein is essential for muscle repair" in explanation


class TestGraniteService:
    @patch("ibm_watsonx_ai.foundation_models.ModelInference")
    @patch("ibm_watsonx_ai.APIClient")
    @patch("ibm_watsonx_ai.Credentials")
    def test_generate_text_returns_stripped_string(
        self,
        mock_creds: MagicMock,
        mock_client: MagicMock,
        mock_model_cls: MagicMock,
    ) -> None:
        mock_instance = MagicMock()
        mock_instance.generate_text.return_value = "  Eat more vegetables.  "
        mock_model_cls.return_value = mock_instance

        from backend.services.granite_service import generate_text

        result = generate_text("What should I eat?")
        assert result == "Eat more vegetables."

    @patch("ibm_watsonx_ai.foundation_models.ModelInference")
    @patch("ibm_watsonx_ai.APIClient")
    @patch("ibm_watsonx_ai.Credentials")
    def test_generate_text_raises_runtime_error_on_failure(
        self,
        mock_creds: MagicMock,
        mock_client: MagicMock,
        mock_model_cls: MagicMock,
    ) -> None:
        mock_instance = MagicMock()
        mock_instance.generate_text.side_effect = Exception("API timeout")
        mock_model_cls.return_value = mock_instance

        from backend.services.granite_service import generate_text

        with pytest.raises(RuntimeError, match="Granite inference error"):
            generate_text("Some prompt")
