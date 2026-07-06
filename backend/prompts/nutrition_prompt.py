"""Nutrition assistant system prompt and prompt-building helpers."""

_SYSTEM_PROMPT = """You are NutriGenie, an expert AI nutrition assistant powered by IBM Granite.

Your role:
- Answer nutrition, diet, and food-related questions with accuracy and empathy.
- Always provide a clear explanation for every recommendation you make.
- Cite the nutritional science principle behind each answer.
- Be concise, warm, and easy to understand.
- Never provide medical diagnoses or replace a licensed dietitian.
- If a question is outside nutrition/health, politely redirect the user.

Response format (always follow this structure):
1. Direct answer to the question.
2. Nutritional explanation: the science or evidence behind the answer.
3. Practical tip: one actionable step the user can take today.

Keep responses under 300 words unless a detailed meal plan is requested."""


def build_chat_prompt(user_message: str, history: list[dict]) -> str:
    """
    Construct the full prompt string for a single-turn chat request.

    Args:
        user_message: The latest message from the user.
        history:      Prior conversation turns as dicts with 'role' and 'content'.

    Returns:
        A formatted prompt string ready to send to Granite.
    """
    lines: list[str] = [_SYSTEM_PROMPT, ""]

    for turn in history[-10:]:  # cap context at 10 prior turns
        role = turn.get("role", "user").capitalize()
        content = turn.get("content", "").strip()
        if content:
            lines.append(f"{role}: {content}")

    lines.append(f"User: {user_message}")
    lines.append("NutriGenie:")

    return "\n".join(lines)


def extract_explanation(response_text: str) -> str:
    """
    Pull the 'Nutritional explanation' section out of the model response,
    or return a generic fallback if the section is missing.
    """
    lower = response_text.lower()
    markers = ["nutritional explanation:", "explanation:", "science:"]
    for marker in markers:
        idx = lower.find(marker)
        if idx != -1:
            snippet = response_text[idx:].split("\n")[0].replace(marker, "").strip()
            if snippet:
                return snippet
    return "This recommendation is grounded in evidence-based nutrition science."
