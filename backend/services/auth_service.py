"""Authentication service: password hashing, JWT token creation/validation."""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

from backend.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,128}$"
)


def validate_password_strength(password: str) -> None:
    """Raise ValueError if the password does not meet complexity requirements."""
    if not _PASSWORD_RE.match(password):
        raise ValueError(
            "Password must be 8–128 characters and include at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _secret() -> str:
    return settings.effective_secret_key()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, _secret(), algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.refresh_token_expire_minutes
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, _secret(), algorithm=settings.algorithm)


def decode_token(token: str, expected_type: str = "access") -> Optional[dict]:
    try:
        payload = jwt.decode(token, _secret(), algorithms=[settings.algorithm])
        if payload.get("type") != expected_type:
            return None
        return payload
    except JWTError:
        return None
