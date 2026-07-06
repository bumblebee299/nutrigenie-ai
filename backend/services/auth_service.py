"""Authentication service — JWT creation/validation and password hashing."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import structlog
from jose import JWTError, jwt

from backend.api.config import settings

logger = structlog.get_logger(__name__)

# Token types embedded in the JWT payload to prevent misuse
_ACCESS_TOKEN_TYPE = "access"
_REFRESH_TOKEN_TYPE = "refresh"


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    # bcrypt silently truncates at 72 bytes — pre-hash with SHA-256 to support
    # arbitrarily long passwords while keeping the bcrypt security properties.
    import hashlib, base64
    digest = base64.b64encode(hashlib.sha256(plain.encode()).digest())
    return bcrypt.hashpw(digest, bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    import hashlib, base64
    digest = base64.b64encode(hashlib.sha256(plain.encode()).digest())
    return bcrypt.checkpw(digest, hashed.encode())


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """Internal helper that signs a JWT with the configured secret key."""
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_access_token(user_id: str) -> str:
    """Return a short-lived access JWT for the given user ID."""
    return _create_token(
        subject=user_id,
        token_type=_ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    """Return a long-lived refresh JWT for the given user ID."""
    return _create_token(
        subject=user_id,
        token_type=_REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: str) -> str:
    """
    Validate *token* and return its subject (user ID).

    Raises:
        ValueError: if the token is invalid, expired, or of the wrong type.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError as exc:
        logger.warning("JWT decode failed", error=str(exc))
        raise ValueError("Invalid or expired token.") from exc

    if payload.get("type") != expected_type:
        raise ValueError(f"Expected token type '{expected_type}', got '{payload.get('type')}'.")

    subject: Optional[str] = payload.get("sub")
    if not subject:
        raise ValueError("Token missing subject claim.")

    return subject


def decode_access_token(token: str) -> str:
    """Validate an access JWT and return the user ID."""
    return decode_token(token, _ACCESS_TOKEN_TYPE)


def decode_refresh_token(token: str) -> str:
    """Validate a refresh JWT and return the user ID."""
    return decode_token(token, _REFRESH_TOKEN_TYPE)
