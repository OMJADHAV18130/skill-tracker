"""Authentication and user schemas."""

from __future__ import annotations

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,64}$")
PASSWORD_MIN_LENGTH = 8


class UserCreate(BaseModel):
    email: EmailStr = Field(..., examples=["learner@example.com"])
    username: str = Field(..., min_length=3, max_length=64)
    full_name: str | None = Field(default=None, max_length=160)
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=128)

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str) -> str:
        value = value.strip()
        if not USERNAME_RE.match(value):
            raise ValueError(
                "Username may only contain letters, numbers, dots, dashes and underscores "
                "(3-64 characters)"
            )
        return value

    @field_validator("email")
    @classmethod
    def _normalise_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("full_name")
    @classmethod
    def _strip_name(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def _normalise_email(cls, value: str) -> str:
        return value.strip().lower()


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=160)
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=64)

    @field_validator("email")
    @classmethod
    def _normalise_email(cls, value: EmailStr | None) -> EmailStr | None:
        return value.strip().lower() if value else value

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not USERNAME_RE.match(value):
            raise ValueError("Invalid username")
        return value


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token lifetime in seconds")
    user: UserRead


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10, max_length=512)


class LogoutRequest(BaseModel):
    refresh_token: str | None = Field(default=None, max_length=512)
    all_sessions: bool = Field(
        default=False, description="Revoke every refresh token for the current user"
    )
