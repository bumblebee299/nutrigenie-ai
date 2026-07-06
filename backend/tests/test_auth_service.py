"""Unit tests for the authentication service layer."""

import pytest
from unittest.mock import MagicMock, patch

from backend.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plain_text(self) -> None:
        hashed = hash_password("secret123")
        assert hashed != "secret123"

    def test_correct_password_verifies(self) -> None:
        hashed = hash_password("mysecurepassword")
        assert verify_password("mysecurepassword", hashed) is True

    def test_wrong_password_fails_verification(self) -> None:
        hashed = hash_password("mysecurepassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_empty_password_verifies_against_its_own_hash(self) -> None:
        hashed = hash_password("")
        assert verify_password("", hashed) is True


class TestJWTTokens:
    def test_access_token_roundtrip(self) -> None:
        token = create_access_token("user-001")
        user_id = decode_access_token(token)
        assert user_id == "user-001"

    def test_refresh_token_roundtrip(self) -> None:
        token = create_refresh_token("user-002")
        user_id = decode_refresh_token(token)
        assert user_id == "user-002"

    def test_access_token_rejected_as_refresh(self) -> None:
        token = create_access_token("user-003")
        with pytest.raises(ValueError, match="Expected token type"):
            decode_refresh_token(token)

    def test_refresh_token_rejected_as_access(self) -> None:
        token = create_refresh_token("user-004")
        with pytest.raises(ValueError, match="Expected token type"):
            decode_access_token(token)

    def test_invalid_token_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid or expired token"):
            decode_access_token("not.a.valid.token")

    def test_tampered_token_raises_value_error(self) -> None:
        token = create_access_token("user-005")
        tampered = token[:-4] + "XXXX"
        with pytest.raises(ValueError):
            decode_access_token(tampered)
