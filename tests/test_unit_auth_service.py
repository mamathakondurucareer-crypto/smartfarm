"""Unit tests for authentication service functions."""

import pytest
from backend.services.auth_service import hash_password, verify_password, create_access_token, decode_token


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = hash_password("mypassword")
        assert isinstance(hashed, str)

    def test_hash_password_not_plaintext(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"

    def test_verify_password_correct(self):
        hashed = hash_password("correctpass")
        assert verify_password("correctpass", hashed) is True

    def test_verify_password_wrong(self):
        hashed = hash_password("correctpass")
        assert verify_password("wrongpass", hashed) is False

    def test_hash_is_unique_per_call(self):
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        assert h1 != h2  # bcrypt uses random salt


class TestJWTTokens:
    def test_create_token_returns_string(self):
        token = create_access_token({"sub": "1", "role": "admin"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        token = create_access_token({"sub": "42", "role": "manager"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["role"] == "manager"

    def test_decode_invalid_token_returns_none(self):
        result = decode_token("not.a.valid.token")
        assert result is None

    def test_decode_tampered_token_returns_none(self):
        token = create_access_token({"sub": "1"})
        tampered = token[:-5] + "XXXXX"
        assert decode_token(tampered) is None

    def test_token_contains_expiry(self):
        token = create_access_token({"sub": "1"})
        payload = decode_token(token)
        assert payload is not None
        assert "exp" in payload
