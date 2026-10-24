"""Health and readiness probes."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import check_database

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
def health() -> dict[str, str]:
    """The process is alive. Does not touch the database."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready", summary="Readiness probe")
def readiness() -> JSONResponse:
    """The process is ready when it can reach the database."""
    database_ok = check_database()
    body = {
        "status": "ready" if database_ok else "not_ready",
        "database": "up" if database_ok else "down",
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return JSONResponse(
        status_code=(
            status.HTTP_200_OK if database_ok else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content=body,
    )
