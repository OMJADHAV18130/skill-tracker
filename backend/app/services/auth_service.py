"""Authentication and account service."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    decode_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.db.seed import seed_user_content
from app.models.user import User
from app.repositories import user_repo
from app.schemas.user import UserCreate

logger = logging.getLogger("devpath.auth")


def register(db: Session, payload: UserCreate) -> User:
    """Create a new account and seed its personal roadmap state."""
    if user_repo.email_exists(db, payload.email):
        raise ConflictError("An account with this email already exists", code="email_taken")
    if user_repo.username_exists(db, payload.username):
        raise ConflictError("This username is already taken", code="username_taken")

    user = user_repo.create_user(
        db,
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    # New accounts get their own progress rows, preferences and projects.
    seed_user_content(db, user)
    db.commit()
    db.refresh(user)
    logger.info("Registered user id=%s username=%s", user.id, user.username)
    return user


def authenticate(db: Session, *, email: str, password: str) -> User:
    user = user_repo.get_by_email(db, email)
    if user is None:
        # Run a dummy verification to keep the timing roughly constant.
        verify_password(password, "$2b$12$" + "." * 53)
        raise UnauthorizedError("Incorrect email or password", code="invalid_credentials")
    if not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password", code="invalid_credentials")
    if not user.is_active:
        raise UnauthorizedError("This account is disabled", code="account_disabled")
    return user


def issue_tokens(db: Session, user: User) -> tuple[str, str]:
    """Create an access token and a rotating refresh token."""
    access_token = create_access_token(user.id, extra_claims={"username": user.username})
    refresh_token = generate_refresh_token()
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    user_repo.store_refresh_token(
        db, user_id=user.id, token_hash=hash_token(refresh_token), expires_at=expires_at
    )
    db.commit()
    return access_token, refresh_token


def access_token_for(user: User) -> str:
    return create_access_token(user.id, extra_claims={"username": user.username})


def refresh_tokens(db: Session, refresh_token: str) -> tuple[User, str, str]:
    """Validate a refresh token and issue a new pair (rotating the refresh token)."""
    record = user_repo.get_refresh_token(db, hash_token(refresh_token))
    if record is None or record.revoked_at is not None:
        raise UnauthorizedError("Invalid refresh token", code="invalid_refresh_token")
    if record.expires_at < datetime.now(UTC):
        raise UnauthorizedError("Refresh token expired", code="refresh_token_expired")

    user = user_repo.get_by_id(db, record.user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Invalid refresh token", code="invalid_refresh_token")

    # Rotate: the old token is revoked as soon as a new one is issued.
    user_repo.revoke_refresh_token(db, record)
    access_token = create_access_token(user.id, extra_claims={"username": user.username})
    new_refresh = generate_refresh_token()
    user_repo.store_refresh_token(
        db,
        user_id=user.id,
        token_hash=hash_token(new_refresh),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.commit()
    return user, access_token, new_refresh


def logout(db: Session, user: User, refresh_token: str | None, all_sessions: bool = False) -> None:
    if all_sessions:
        user_repo.revoke_all_refresh_tokens(db, user.id)
        db.commit()
        return
    if refresh_token:
        record = user_repo.get_refresh_token(db, hash_token(refresh_token))
        if record is not None and record.user_id == user.id:
            user_repo.revoke_refresh_token(db, record)
            db.commit()


def user_from_access_token(db: Session, token: str) -> User:
    """Resolve the user from a verified access token."""
    import jwt

    try:
        payload = decode_token(token, expected_type="access")
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired access token", code="invalid_token") from exc

    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError("Invalid access token", code="invalid_token")
    try:
        user_id = uuid.UUID(str(subject))
    except ValueError as exc:
        raise UnauthorizedError("Invalid access token", code="invalid_token") from exc

    user = user_repo.get_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError("Account no longer exists", code="user_not_found")
    if not user.is_active:
        raise UnauthorizedError("This account is disabled", code="account_disabled")
    return user
