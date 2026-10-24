"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.core.errors import UnauthorizedError
from app.core.security import hash_password
from app.repositories import user_repo
from app.schemas.common import Message
from app.schemas.user import (
    LogoutRequest,
    PasswordChange,
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserLogin,
    UserRead,
    UserUpdate,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_pair(db, user) -> TokenPair:
    access_token, refresh_token = auth_service.issue_tokens(db, user)
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserRead.model_validate(user),
    )


@router.post(
    "/register",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
    summary="Create an account",
)
def register(payload: UserCreate, db: DbSession) -> TokenPair:
    """Register a new learner and return a fresh token pair."""
    user = auth_service.register(db, payload)
    return _token_pair(db, user)


@router.post("/login", response_model=TokenPair, summary="Sign in with email and password")
def login(payload: UserLogin, db: DbSession) -> TokenPair:
    user = auth_service.authenticate(db, email=payload.email, password=payload.password)
    user_repo.touch_login(db, user)
    db.commit()
    return _token_pair(db, user)


@router.post("/refresh", response_model=TokenPair, summary="Rotate a refresh token")
def refresh(payload: RefreshRequest, db: DbSession) -> TokenPair:
    user, access_token, refresh_token = auth_service.refresh_tokens(db, payload.refresh_token)
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserRead.model_validate(user),
    )


@router.post("/logout", response_model=Message, summary="Sign out and revoke refresh tokens")
def logout(payload: LogoutRequest, db: DbSession, current_user: CurrentUser) -> Message:
    auth_service.logout(db, current_user, payload.refresh_token, payload.all_sessions)
    return Message(message="Signed out successfully")


@router.get("/me", response_model=UserRead, summary="Current account")
def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead, summary="Update the current account")
def update_me(
    payload: UserUpdate, db: DbSession, current_user: CurrentUser
) -> UserRead:
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"]:
        if user_repo.email_exists(db, data["email"]) and data["email"] != current_user.email:
            from app.core.errors import ConflictError

            raise ConflictError("An account with this email already exists", code="email_taken")
        current_user.email = data["email"]
    if "username" in data and data["username"]:
        if (
            user_repo.username_exists(db, data["username"])
            and data["username"] != current_user.username
        ):
            from app.core.errors import ConflictError

            raise ConflictError("This username is already taken", code="username_taken")
        current_user.username = data["username"]
    if "full_name" in data:
        current_user.full_name = data["full_name"]
    db.commit()
    db.refresh(current_user)
    return UserRead.model_validate(current_user)


@router.post(
    "/change-password",
    response_model=Message,
    summary="Change the current account password",
)
def change_password(
    payload: PasswordChange, db: DbSession, current_user: CurrentUser
) -> Message:
    from app.core.security import verify_password

    if not verify_password(payload.current_password, current_user.hashed_password):
        raise UnauthorizedError("Current password is incorrect", code="invalid_credentials")
    current_user.hashed_password = hash_password(payload.new_password)
    auth_service.logout(db, current_user, None, all_sessions=True)
    db.commit()
    return Message(message="Password updated. Please sign in again.")
