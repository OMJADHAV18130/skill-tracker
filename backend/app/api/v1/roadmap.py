"""Roadmap endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.roadmap import (
    PhaseListResponse,
    TopicChecklistItemCreate,
    TopicChecklistItemRead,
    TopicChecklistItemUpdate,
    TopicNavigation,
    TopicNoteCreate,
    TopicNoteRead,
    TopicNoteUpdate,
    TopicProgressUpdate,
    TopicRead,
)
from app.services import roadmap_service

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.get(
    "/phases",
    response_model=PhaseListResponse,
    summary="All roadmap phases with the current user's progress",
)
def list_phases(
    db: DbSession,
    current_user: CurrentUser,
    track: str = Query(default="core", pattern="^(core|dsa)$"),
) -> PhaseListResponse:
    """One roadmap track (core Backend + DevOps, or the parallel DSA track)."""
    return roadmap_service.list_phases(db, current_user.id, track=track)


@router.get(
    "/topics/{topic_id}",
    response_model=TopicRead,
    summary="A single topic with progress, notes, checklist and resources",
)
def get_topic(topic_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> TopicRead:
    return roadmap_service.get_topic(db, current_user.id, topic_id)


@router.patch(
    "/topics/{topic_id}/progress",
    response_model=TopicRead,
    summary="Update progress for a topic (status, priority, rating)",
)
def update_progress(
    topic_id: uuid.UUID,
    payload: TopicProgressUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> TopicRead:
    """Mark a topic complete, in progress or re-open it.

    Progress is derived from the current status so a topic that is re-opened
    and completed again is never counted twice.
    """
    return roadmap_service.update_topic_progress(db, current_user.id, topic_id, payload)


@router.get(
    "/topics/{topic_id}/navigation",
    response_model=TopicNavigation,
    summary="Previous and next topic for sequential learning",
)
def topic_navigation(
    topic_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> TopicNavigation:
    return roadmap_service.topic_navigation(db, current_user.id, topic_id)


@router.get(
    "/topics/{topic_id}/notes",
    response_model=list[TopicNoteRead],
    summary="Personal notes for a topic",
)
def list_notes(topic_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> list[TopicNoteRead]:
    return roadmap_service.list_notes(db, current_user.id, topic_id)


@router.post(
    "/topics/{topic_id}/notes",
    response_model=TopicNoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a note to a topic",
)
def create_note(
    topic_id: uuid.UUID,
    payload: TopicNoteCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> TopicNoteRead:
    return roadmap_service.create_note(db, current_user.id, topic_id, payload)


@router.patch(
    "/notes/{note_id}",
    response_model=TopicNoteRead,
    summary="Update a note",
)
def update_note(
    note_id: uuid.UUID,
    payload: TopicNoteUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> TopicNoteRead:
    return roadmap_service.update_note(db, current_user.id, note_id, payload)


@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
)
def delete_note(note_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> None:
    roadmap_service.delete_note(db, current_user.id, note_id)


@router.get(
    "/topics/{topic_id}/checklist",
    response_model=list[TopicChecklistItemRead],
    summary="Personal checklist for a topic",
)
def list_checklist(
    topic_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> list[TopicChecklistItemRead]:
    return roadmap_service.list_checklist(db, current_user.id, topic_id)


@router.post(
    "/topics/{topic_id}/checklist",
    response_model=TopicChecklistItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a checklist item to a topic",
)
def create_checklist_item(
    topic_id: uuid.UUID,
    payload: TopicChecklistItemCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> TopicChecklistItemRead:
    return roadmap_service.create_checklist_item(db, current_user.id, topic_id, payload)


@router.patch(
    "/checklist/{item_id}",
    response_model=TopicChecklistItemRead,
    summary="Update a checklist item",
)
def update_checklist_item(
    item_id: uuid.UUID,
    payload: TopicChecklistItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> TopicChecklistItemRead:
    return roadmap_service.update_checklist_item(db, current_user.id, item_id, payload)


@router.delete(
    "/checklist/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a checklist item",
)
def delete_checklist_item(
    item_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> None:
    roadmap_service.delete_checklist_item(db, current_user.id, item_id)


@router.get(
    "/next",
    response_model=TopicRead | None,
    summary="The next recommended topic",
)
def next_topic(
    db: DbSession,
    current_user: CurrentUser,
    track: str = Query(default="core", pattern="^(core|dsa)$"),
) -> TopicRead | None:
    return roadmap_service.next_recommended_topic(db, current_user.id, track=track)
