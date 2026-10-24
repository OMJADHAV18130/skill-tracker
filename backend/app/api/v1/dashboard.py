"""Dashboard endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.dashboard import DashboardRead
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "",
    response_model=DashboardRead,
    summary="Aggregated dashboard for the signed-in learner",
)
def get_dashboard(db: DbSession, current_user: CurrentUser) -> DashboardRead:
    """Every figure is calculated from the caller's persisted records."""
    return dashboard_service.build_dashboard(db, current_user.id)
