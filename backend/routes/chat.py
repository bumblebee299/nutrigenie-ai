"""AI Chat routes — nutrition Q&A powered by IBM Granite."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_current_user
from backend.models.auth import UserPublic
from backend.models.chat import ChatRequest, ChatResponse, FeedbackRequest
from backend.services.chat_service import answer_nutrition_question, store_feedback

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Ask the AI nutrition assistant a question",
)
async def chat(
    payload: ChatRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> ChatResponse:
    """
    Send a nutrition question to IBM Granite and receive a structured response.

    - The `history` field accepts up to 20 prior turns for multi-turn context.
    - Each response includes a plain-language `explanation` of the reasoning.
    - Use the returned timestamp and message text as the `message_id` for feedback.
    """
    if payload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id in body must match authenticated user.",
        )

    try:
        response = answer_nutrition_question(payload)
    except RuntimeError as exc:
        logger.error("Chat inference failed", user_id=current_user.id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc

    logger.info("Chat response delivered", user_id=current_user.id)
    return response


@router.post(
    "/feedback",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Submit feedback on an AI recommendation",
)
async def submit_feedback(
    payload: FeedbackRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> None:
    """
    Record whether the user found a chat reply helpful.

    Feedback is stored in IBM Cloudant and used to improve future recommendations.
    """
    if payload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id in body must match authenticated user.",
        )

    try:
        store_feedback(payload)
    except Exception as exc:
        logger.error("Feedback storage failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store feedback.",
        ) from exc
