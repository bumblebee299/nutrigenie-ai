"""IBM Granite / watsonx.ai inference service."""

import structlog

logger = structlog.get_logger(__name__)


def _get_model():  # type: ignore[return]
    """
    Create and return an authenticated Granite ModelInference instance.

    Raises:
        RuntimeError: if WATSONX_API_KEY or WATSONX_PROJECT_ID are not configured.
    """
    from backend.api.config import settings

    if not settings.WATSONX_API_KEY or not settings.WATSONX_PROJECT_ID:
        raise RuntimeError(
            "IBM watsonx.ai is not configured. "
            "Set WATSONX_API_KEY and WATSONX_PROJECT_ID in your .env file."
        )

    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

    credentials = Credentials(
        url=settings.WATSONX_URL,
        api_key=settings.WATSONX_API_KEY,
    )
    client = APIClient(credentials=credentials)
    return ModelInference(
        model_id=settings.GRANITE_MODEL_ID,
        api_client=client,
        project_id=settings.WATSONX_PROJECT_ID,
        params={
            GenParams.MAX_NEW_TOKENS: 1024,
            GenParams.MIN_NEW_TOKENS: 20,
            GenParams.TEMPERATURE: 0.7,
            GenParams.TOP_P: 0.9,
            GenParams.REPETITION_PENALTY: 1.1,
            GenParams.STOP_SEQUENCES: ["<|endoftext|>", "User:", "Human:"],
        },
    )


def generate_text(prompt: str) -> str:
    """
    Send a prompt to Granite and return the generated text.

    Args:
        prompt: The fully constructed prompt string.

    Returns:
        The model's generated text with leading/trailing whitespace stripped.

    Raises:
        RuntimeError: if credentials are missing or the model call fails.
    """
    try:
        model = _get_model()
        result = model.generate_text(prompt=prompt)
        logger.info("Granite generation complete", prompt_length=len(prompt))
        return result.strip()
    except RuntimeError:
        raise
    except Exception as exc:
        logger.error("Granite generation failed", error=str(exc))
        raise RuntimeError(f"Granite inference error: {exc}") from exc
