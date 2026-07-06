"""User service — Cloudant CRUD operations for the users collection."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from ibmcloudant.cloudant_v1 import CloudantV1

from backend.api.config import settings
from backend.database.cloudant import cloudant_client
from backend.models.auth import UserPublic
from backend.models.profile import ProfileResponse, ProfileUpdate
from backend.services.auth_service import hash_password

logger = structlog.get_logger(__name__)

_DB = settings.CLOUDANT_DB_USERS


def _to_user_public(doc: dict) -> UserPublic:
    return UserPublic(
        id=doc["_id"],
        name=doc["name"],
        email=doc["email"],
        created_at=datetime.fromisoformat(doc["created_at"]),
        is_active=doc.get("is_active", True),
    )


def _to_profile_response(doc: dict) -> ProfileResponse:
    return ProfileResponse(
        id=doc["_id"],
        name=doc["name"],
        email=doc["email"],
        age=doc.get("age"),
        height_cm=doc.get("height_cm"),
        weight_kg=doc.get("weight_kg"),
        gender=doc.get("gender"),
        goal=doc.get("goal"),
        diseases=doc.get("diseases", []),
        allergies=doc.get("allergies", []),
        cuisine_preference=doc.get("cuisine_preference", []),
        lifestyle=doc.get("lifestyle"),
        created_at=datetime.fromisoformat(doc["created_at"]),
        updated_at=datetime.fromisoformat(doc["updated_at"]) if doc.get("updated_at") else None,
    )


def get_user_by_email(email: str) -> Optional[dict]:
    """Fetch a raw Cloudant document by email address using a Mango selector."""
    result = cloudant_client.post_find(
        db=_DB,
        selector={"email": {"$eq": email}},
        limit=1,
    ).get_result()
    docs = result.get("docs", [])
    return docs[0] if docs else None


def get_user_by_id(user_id: str) -> Optional[dict]:
    """Fetch a raw Cloudant document by document ID."""
    try:
        doc = cloudant_client.get_document(db=_DB, doc_id=user_id).get_result()
        return doc
    except Exception:
        return None


def create_user(name: str, email: str, password: str) -> UserPublic:
    """
    Persist a new user document to Cloudant and return its public representation.

    Raises:
        ValueError: if a user with the given email already exists.
    """
    if get_user_by_email(email):
        raise ValueError("An account with this email address already exists.")

    now = datetime.now(tz=timezone.utc).isoformat()
    user_id = str(uuid.uuid4())

    doc = {
        "_id": user_id,
        "name": name,
        "email": email,
        "hashed_password": hash_password(password),
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    cloudant_client.put_document(db=_DB, doc_id=user_id, document=doc)
    logger.info("User created", user_id=user_id, email=email)
    return _to_user_public(doc)


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """
    Verify credentials and return the raw user document on success.

    Returns:
        The user document if credentials are valid, else None.
    """
    from backend.services.auth_service import verify_password

    doc = get_user_by_email(email)
    if not doc:
        return None
    if not verify_password(password, doc.get("hashed_password", "")):
        return None
    if not doc.get("is_active", True):
        return None
    return doc


def get_profile(user_id: str) -> ProfileResponse:
    """
    Return the full profile for a user.

    Raises:
        ValueError: if the user is not found.
    """
    doc = get_user_by_id(user_id)
    if not doc:
        raise ValueError(f"User '{user_id}' not found.")
    return _to_profile_response(doc)


def update_profile(user_id: str, payload: ProfileUpdate) -> ProfileResponse:
    """
    Apply a partial update to the user document and return the updated profile.

    Raises:
        ValueError: if the user is not found.
    """
    doc = get_user_by_id(user_id)
    if not doc:
        raise ValueError(f"User '{user_id}' not found.")

    updates = payload.model_dump(exclude_none=True)
    doc.update(updates)
    doc["updated_at"] = datetime.now(tz=timezone.utc).isoformat()

    cloudant_client.put_document(db=_DB, doc_id=user_id, document=doc)
    logger.info("Profile updated", user_id=user_id, fields=list(updates.keys()))
    return _to_profile_response(doc)
