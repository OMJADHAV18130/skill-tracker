"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.db.session import get_db
from app.models.user import User
from app.services import auth_service

bearer_scheme = HTTPBearer(auto_error=False, description="JWT access token")

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    request: Request,
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    """Resolve the current user from the ``Authorization: Bearer <token>`` header.

    The user identity always comes from the verified token - never from a
    user id supplied by the client.
    """
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Authentication required", code="missing_token")
    user = auth_service.user_from_access_token(db, credentials.credentials)
    request.state.user_id = str(user.id)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


class Pagination:
    """Simple page/page_size pagination dependency."""

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="1-based page number"),
        page_size: int = Query(default=50, ge=1, le=200, description="Items per page"),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


PageDep = Annotated[Pagination, Depends(Pagination)]
