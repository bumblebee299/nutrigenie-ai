"""Chat service — orchestrates Granite inference and Cloudant persistence."""

import uuid
from datetime import datetime, timezone

import structlog

from backend.api.config import settings
from backend.database.cloudant import cloudant_client
from backend.models.chat import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
)
from backend.prompts.nutrition_prompt import build_chat_prompt, extract_explanation
from backend.services.granite_service import generate_text

logger = structlog.get_logger(__name__)

_FEEDBACK_DB = settings.CLOUDANT_DB_FEEDBACK


def answer_nutrition_question(request: ChatRequest) -> ChatResponse:
    """
    Run the full chat pipeline:

    1. Construct the prompt from history + new message.
    2. Call IBM Granite for a response.
    3. Extract an explanation from the response.
    4. Return a structured ChatResponse.

    Args:
        request: Validated chat payload from the route.

    Returns:
        ChatResponse with reply, explanation, and timestamp.

    Raises:
        RuntimeError: propagated from granite_service on inference failure.
    """
    history = [{"role": m.role.value, "content": m.content} for m in request.history]
    prompt = build_chat_prompt(request.message, history)

    logger.info(
        "Sending chat prompt to Granite",
        user_id=request.user_id,
        history_turns=len(history),
    )

    reply = generate_text(prompt)
    explanation = extract_explanation(reply)
    now = datetime.now(tz=timezone.utc)

    return ChatResponse(
        reply=reply,
        explanation=explanation,
        sources=[],
        timestamp=now,
    )


def store_feedback(feedback: FeedbackRequest) -> None:
    """
    Persist a user feedback document to the Cloudant feedback collection.

    The stored document is also used by future tasks to improve recommendations.
    """
    doc_id = str(uuid.uuid4())
    doc = {
        "_id": doc_id,
        "message_id": feedback.message_id,
        "user_id": feedback.user_id,
        "helpful": feedback.helpful,
        "comment": feedback.comment,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
    }
    cloudant_client.put_document(db=_FEEDBACK_DB, doc_id=doc_id, document=doc)
    logger.info(
        "Feedback stored",
        doc_id=doc_id,
        user_id=feedback.user_id,
        helpful=feedback.helpful,
    )
