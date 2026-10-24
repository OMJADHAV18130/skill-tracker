"""Settings, export, import and reset endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CurrentUser, DbSession
from app.core.errors import ValidationError
from app.schemas.common import Message
from app.schemas.preference import (
    DsaPauseRequest,
    ExportPayload,
    ImportPreview,
    ImportRequest,
    PreferenceRead,
    PreferenceUpdate,
)
from app.services import preference_service

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=PreferenceRead, summary="Read the user's preferences")
def get_preferences(db: DbSession, current_user: CurrentUser) -> PreferenceRead:
    return preference_service.get_preferences(db, current_user.id)


@router.patch("", response_model=PreferenceRead, summary="Update the user's preferences")
def update_preferences(
    payload: PreferenceUpdate, db: DbSession, current_user: CurrentUser
) -> PreferenceRead:
    return preference_service.update_preferences(db, current_user.id, payload)


@router.post(
    "/dsa/pause",
    response_model=PreferenceRead,
    summary="Pause the parallel DSA track during exams",
)
def pause_dsa(
    db: DbSession,
    current_user: CurrentUser,
    payload: DsaPauseRequest | None = None,
) -> PreferenceRead:
    resume_on = payload.resume_on if payload is not None else None
    return preference_service.pause_dsa(db, current_user.id, resume_on)


@router.post(
    "/dsa/resume",
    response_model=PreferenceRead,
    summary="Resume the parallel DSA track",
)
def resume_dsa(db: DbSession, current_user: CurrentUser) -> PreferenceRead:
    return preference_service.resume_dsa(db, current_user.id)


@router.get(
    "/export.json",
    summary="Export all learning progress as JSON",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}}},
)
def export_json(db: DbSession, current_user: CurrentUser) -> Response:
    payload = preference_service.build_export(db, current_user.id)
    return Response(
        content=payload.model_dump_json(indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=devpath-progress.json"},
    )


@router.get(
    "/export.csv",
    summary="Export topic progress as CSV",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}}},
)
def export_csv(db: DbSession, current_user: CurrentUser) -> Response:
    content = preference_service.export_csv(db, current_user.id)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=devpath-progress.csv"},
    )


@router.post(
    "/import/validate",
    response_model=ImportPreview,
    summary="Validate a progress backup without applying it",
)
def validate_import(payload: ExportPayload) -> ImportPreview:
    return preference_service.validate_export(payload)


@router.post(
    "/import",
    summary="Import a previously exported progress backup",
)
def import_backup(
    payload: ImportRequest, db: DbSession, current_user: CurrentUser
) -> Message:
    """Import a backup. Requires ``confirm=true`` after the user confirms."""
    if not payload.confirm:
        raise ValidationError(
            "The import needs an explicit confirmation", code="confirmation_required"
        )
    counters = preference_service.import_export(
        db, current_user.id, payload.payload, mode=payload.mode
    )
    summary = ", ".join(f"{key}={value}" for key, value in counters.items() if value)
    return Message(message=f"Import complete. {summary or 'Nothing to import'}")


@router.post(
    "/reset",
    response_model=Message,
    status_code=status.HTTP_200_OK,
    summary="Reset all progress (requires confirmation)",
)
def reset_progress(
    db: DbSession,
    current_user: CurrentUser,
    confirm: bool = Query(
        default=False, description="Must be true - confirms the destructive action"
    ),
) -> Message:
    """Delete every personal progress record and restore the default projects."""
    if not confirm:
        raise ValidationError(
            "Resetting progress requires an explicit confirmation", code="confirmation_required"
        )
    counters = preference_service.reset_progress(db, current_user.id)
    summary = ", ".join(f"{key}={value}" for key, value in counters.items() if value)
    return Message(message=f"Progress reset. {summary or 'Nothing to remove'}")
