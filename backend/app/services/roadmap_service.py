"""Roadmap service: phases, topics, progress, notes and checklists."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.models.roadmap import TRACKS, TopicStatus
from app.repositories import roadmap_repo
from app.schemas.roadmap import (
    PhaseListResponse,
    PhaseRead,
    ResourceBrief,
    TopicChecklistItemCreate,
    TopicChecklistItemRead,
    TopicChecklistItemUpdate,
    TopicNavigation,
    TopicNoteCreate,
    TopicNoteRead,
    TopicNoteUpdate,
    TopicProgressRead,
    TopicProgressUpdate,
    TopicRead,
)


def _progress_read(
    db: Session,
    user_id: uuid.UUID,
    topic_id: uuid.UUID,
    progress_row,
) -> TopicProgressRead:
    notes = roadmap_repo.list_notes(db, user_id, topic_id)
    checklist = roadmap_repo.list_checklist(db, user_id, topic_id)
    if progress_row is None:
        return TopicProgressRead(
            status=TopicStatus.NOT_STARTED,
            notes=[TopicNoteRead.model_validate(n) for n in notes],
            checklist=[TopicChecklistItemRead.model_validate(c) for c in checklist],
        )
    return TopicProgressRead(
        status=progress_row.status,
        priority=progress_row.priority,
        rating=progress_row.rating,
        started_at=progress_row.started_at,
        completed_at=progress_row.completed_at,
        notes=[TopicNoteRead.model_validate(n) for n in notes],
        checklist=[TopicChecklistItemRead.model_validate(c) for c in checklist],
    )


def _topic_read(
    db: Session,
    user_id: uuid.UUID,
    topic,
    progress_by_topic: dict,
) -> TopicRead:
    resources = [
        ResourceBrief.model_validate(link.resource)
        for link in topic.resource_links
        if link.resource is not None
    ]
    return TopicRead(
        id=topic.id,
        phase_id=topic.phase_id,
        slug=topic.slug,
        title=topic.title,
        description=topic.description,
        category=topic.category,
        estimated_minutes=topic.estimated_minutes,
        order_index=topic.order_index,
        track=topic.phase.track if topic.phase is not None else "core",
        subtopics=list(topic.subtopics or []),
        is_key_topic=topic.is_key_topic,
        progress=_progress_read(db, user_id, topic.id, progress_by_topic.get(topic.id)),
        resources=resources,
    )


def list_phases(db: Session, user_id: uuid.UUID, track: str = "core") -> PhaseListResponse:
    """Phases for one track with the user's own progress merged in."""
    if track not in TRACKS:
        raise ValidationError("Unknown roadmap track", code="unknown_track")
    phases = roadmap_repo.list_phases(db, track=track)
    topics = roadmap_repo.list_topics(db, track=track)
    progress_by_topic = roadmap_repo.progress_counts_by_topic(db, user_id)

    topics_by_phase: dict = {}
    for topic in topics:
        topics_by_phase.setdefault(topic.phase_id, []).append(topic)

    phase_items: list[PhaseRead] = []
    total_topics = 0
    completed_topics = 0

    for phase in phases:
        phase_topics = topics_by_phase.get(phase.id, [])
        completed = 0
        in_progress = 0
        for topic in phase_topics:
            row = progress_by_topic.get(topic.id)
            status = row.status if row else TopicStatus.NOT_STARTED
            if status == TopicStatus.COMPLETED:
                completed += 1
            elif status == TopicStatus.IN_PROGRESS:
                in_progress += 1

        total_topics += len(phase_topics)
        completed_topics += completed

        phase_items.append(
            PhaseRead(
                id=phase.id,
                key=phase.key,
                title=phase.title,
                summary=phase.summary,
                month_label=phase.month_label,
                duration_months=phase.duration_months,
                order_index=phase.order_index,
                track=phase.track,
                project_brief=phase.project_brief,
                accent=phase.accent,
                topic_count=len(phase_topics),
                completed_count=completed,
                in_progress_count=in_progress,
                completion_percentage=round((completed / len(phase_topics) * 100), 2)
                if phase_topics
                else 0.0,
                estimated_minutes=sum(t.estimated_minutes for t in phase_topics),
                status=(
                    "completed"
                    if phase_topics and completed == len(phase_topics)
                    else ("in_progress" if completed or in_progress else "not_started")
                ),
                topics=[
                    _topic_read(db, user_id, topic, progress_by_topic) for topic in phase_topics
                ],
            )
        )

    return PhaseListResponse(
        items=phase_items,
        track=track,
        total_topics=total_topics,
        completed_topics=completed_topics,
        completion_percentage=round((completed_topics / total_topics * 100), 2)
        if total_topics
        else 0.0,
    )


def get_topic(db: Session, user_id: uuid.UUID, topic_id: uuid.UUID) -> TopicRead:
    topic = roadmap_repo.get_topic(db, topic_id)
    if topic is None:
        raise NotFoundError("Topic not found", code="topic_not_found")
    progress_by_topic = roadmap_repo.progress_counts_by_topic(db, user_id)
    return _topic_read(db, user_id, topic, progress_by_topic)


def update_topic_progress(
    db: Session, user_id: uuid.UUID, topic_id: uuid.UUID, payload: TopicProgressUpdate
) -> TopicRead:
    """Update the progress of a topic for the current user.

    Progress is *derived* from the current status, so re-opening and
    re-completing a topic can never inflate the counters.
    """
    topic = roadmap_repo.get_topic(db, topic_id)
    if topic is None:
        raise NotFoundError("Topic not found", code="topic_not_found")

    progress = roadmap_repo.ensure_progress(db, user_id, topic_id)
    now = datetime.now(UTC)

    if payload.priority is not None:
        progress.priority = payload.priority
    if payload.rating is not None:
        progress.rating = payload.rating

    if payload.status is not None:
        target = payload.status
        if target == TopicStatus.COMPLETED:
            if progress.status != TopicStatus.COMPLETED:
                progress.started_at = progress.started_at or now
                progress.completed_at = payload.completed_at or now
            elif payload.completed_at is not None:
                progress.completed_at = payload.completed_at
        elif target == TopicStatus.IN_PROGRESS:
            progress.started_at = progress.started_at or now
            progress.completed_at = None
        else:  # NOT_STARTED - reopen
            progress.completed_at = None
            progress.started_at = None
        progress.status = target

    if payload.started_at is not None:
        progress.started_at = payload.started_at
    if payload.completed_at is not None and progress.status == TopicStatus.COMPLETED:
        progress.completed_at = payload.completed_at

    progress.version += 1
    db.commit()
    db.refresh(progress)
    return get_topic(db, user_id, topic_id)


def topic_navigation(db: Session, user_id: uuid.UUID, topic_id: uuid.UUID) -> TopicNavigation:
    current = roadmap_repo.get_topic(db, topic_id)
    if current is None:
        raise NotFoundError("Topic not found", code="topic_not_found")
    track = current.phase.track if current.phase is not None else "core"
    topics = roadmap_repo.list_topics(db, track=track)
    if not topics:
        raise NotFoundError("Topic not found", code="topic_not_found")
    ids = [t.id for t in topics]
    try:
        index = ids.index(topic_id)
    except ValueError as exc:
        raise NotFoundError("Topic not found", code="topic_not_found") from exc

    progress_by_topic = roadmap_repo.progress_counts_by_topic(db, user_id)
    previous = (
        _topic_read(db, user_id, topics[index - 1], progress_by_topic) if index > 0 else None
    )
    following = (
        _topic_read(db, user_id, topics[index + 1], progress_by_topic)
        if index + 1 < len(topics)
        else None
    )
    return TopicNavigation(
        previous=previous, next=following, position=index + 1, total=len(topics)
    )


def list_notes(db: Session, user_id: uuid.UUID, topic_id: uuid.UUID) -> list[TopicNoteRead]:
    if roadmap_repo.get_topic(db, topic_id) is None:
        raise NotFoundError("Topic not found", code="topic_not_found")
    return [TopicNoteRead.model_validate(n) for n in roadmap_repo.list_notes(db, user_id, topic_id)]


def create_note(
    db: Session, user_id: uuid.UUID, topic_id: uuid.UUID, payload: TopicNoteCreate
) -> TopicNoteRead:
    if roadmap_repo.get_topic(db, topic_id) is None:
        raise NotFoundError("Topic not found", code="topic_not_found")
    note = roadmap_repo.create_note(
        db, user_id=user_id, topic_id=topic_id, content=payload.content
    )
    db.commit()
    db.refresh(note)
    return TopicNoteRead.model_validate(note)


def update_note(
    db: Session, user_id: uuid.UUID, note_id: uuid.UUID, payload: TopicNoteUpdate
) -> TopicNoteRead:
    note = roadmap_repo.get_note(db, user_id, note_id)
    if note is None:
        raise NotFoundError("Note not found", code="note_not_found")
    note.content = payload.content
    db.commit()
    db.refresh(note)
    return TopicNoteRead.model_validate(note)


def delete_note(db: Session, user_id: uuid.UUID, note_id: uuid.UUID) -> None:
    note = roadmap_repo.get_note(db, user_id, note_id)
    if note is None:
        raise NotFoundError("Note not found", code="note_not_found")
    db.delete(note)
    db.commit()


def list_checklist(
    db: Session, user_id: uuid.UUID, topic_id: uuid.UUID
) -> list[TopicChecklistItemRead]:
    if roadmap_repo.get_topic(db, topic_id) is None:
        raise NotFoundError("Topic not found", code="topic_not_found")
    return [
        TopicChecklistItemRead.model_validate(item)
        for item in roadmap_repo.list_checklist(db, user_id, topic_id)
    ]


def create_checklist_item(
    db: Session, user_id: uuid.UUID, topic_id: uuid.UUID, payload: TopicChecklistItemCreate
) -> TopicChecklistItemRead:
    if roadmap_repo.get_topic(db, topic_id) is None:
        raise NotFoundError("Topic not found", code="topic_not_found")
    item = roadmap_repo.create_checklist_item(
        db,
        user_id=user_id,
        topic_id=topic_id,
        title=payload.title,
        is_done=payload.is_done,
    )
    db.commit()
    db.refresh(item)
    return TopicChecklistItemRead.model_validate(item)


def update_checklist_item(
    db: Session, user_id: uuid.UUID, item_id: uuid.UUID, payload: TopicChecklistItemUpdate
) -> TopicChecklistItemRead:
    item = roadmap_repo.get_checklist_item(db, user_id, item_id)
    if item is None:
        raise NotFoundError("Checklist item not found", code="checklist_item_not_found")
    if payload.title is not None:
        item.title = payload.title
    if payload.is_done is not None:
        item.is_done = payload.is_done
    db.commit()
    db.refresh(item)
    return TopicChecklistItemRead.model_validate(item)


def delete_checklist_item(db: Session, user_id: uuid.UUID, item_id: uuid.UUID) -> None:
    item = roadmap_repo.get_checklist_item(db, user_id, item_id)
    if item is None:
        raise NotFoundError("Checklist item not found", code="checklist_item_not_found")
    db.delete(item)
    db.commit()


def next_recommended_topic(
    db: Session, user_id: uuid.UUID, track: str = "core"
) -> TopicRead | None:
    """The next topic to work on: an in-progress topic first, else the first
    topic that has not been started, else the first unfinished topic."""
    topics = roadmap_repo.list_topics(db, track=track)
    if not topics:
        return None
    progress_by_topic = roadmap_repo.progress_counts_by_topic(db, user_id)

    def status_of(topic):
        row = progress_by_topic.get(topic.id)
        return row.status if row else TopicStatus.NOT_STARTED

    in_progress = [t for t in topics if status_of(t) == TopicStatus.IN_PROGRESS]
    not_started = [t for t in topics if status_of(t) == TopicStatus.NOT_STARTED]
    unfinished = [
        t for t in topics if status_of(t) in {TopicStatus.IN_PROGRESS, TopicStatus.NOT_STARTED}
    ]

    candidate = (in_progress or not_started or unfinished or [topics[-1]])[0]
    return _topic_read(db, user_id, candidate, progress_by_topic)


def ensure_topic_exists(db: Session, topic_id: uuid.UUID) -> None:
    if roadmap_repo.get_topic(db, topic_id) is None:
        raise ValidationError("Unknown topic", code="unknown_topic")
