"""Password hashing and JWT helpers."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

BCRYPT_MAX_BYTES = 72


def _password_bytes(password: str) -> bytes:
    encoded = password.encode("utf-8")
    if len(encoded) > BCRYPT_MAX_BYTES:
        # bcrypt silently truncates; hash the SHA-256 of the pre-hash instead so
        # that long passwords still work and remain unique.
        return hashlib.sha256(encoded).hexdigest().encode("ascii")
    return encoded


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt. Never log the input."""
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(_password_bytes(password), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Constant-time verification of a plaintext password against a stored hash."""
    try:
        return bcrypt.checkpw(_password_bytes(password), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str | uuid.UUID,
    *,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(UTC)
    expire = now + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": secrets.token_urlsafe(16),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, *, expected_type: str | None = None) -> dict[str, Any]:
    """Decode + verify a JWT. Raises ``jwt.PyJWTError`` on any problem."""
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    if expected_type and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"Expected token type {expected_type!r}")
    return payload


def generate_refresh_token() -> str:
    """Opaque high-entropy refresh token (only its SHA-256 digest is stored)."""
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def constant_time_equals(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)
