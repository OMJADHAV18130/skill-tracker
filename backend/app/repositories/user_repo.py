"""User related data access."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.user import RefreshToken, User, UserRole


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.strip().lower()))


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def email_exists(db: Session, email: str) -> bool:
    return get_by_email(db, email) is not None


def username_exists(db: Session, username: str) -> bool:
    return get_by_username(db, username) is not None


def create_user(
    db: Session,
    *,
    email: str,
    username: str,
    password_hash: str,
    full_name: str | None = None,
    role: UserRole = UserRole.USER,
) -> User:
    user = User(
        email=email.strip().lower(),
        username=username.strip(),
        full_name=full_name,
        hashed_password=password_hash,
        role=role,
    )
    db.add(user)
    db.flush()
    return user


def touch_login(db: Session, user: User) -> None:
    db.execute(
        update(User).where(User.id == user.id).values(last_login_at=datetime.now(UTC))
    )


def store_refresh_token(
    db: Session, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime
) -> RefreshToken:
    record = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(record)
    db.flush()
    return record


def get_refresh_token(db: Session, token_hash: str) -> RefreshToken | None:
    return db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))


def revoke_refresh_token(db: Session, record: RefreshToken) -> None:
    record.revoked_at = datetime.now(UTC)


def revoke_all_refresh_tokens(db: Session, user_id: uuid.UUID) -> int:
    result = db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    return int(result.rowcount or 0)


def delete_user_cascade(db: Session, user: User) -> None:
    db.delete(user)
    db.flush()
