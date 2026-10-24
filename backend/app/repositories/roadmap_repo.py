"""Roadmap related data access (shared definitions + per-user progress)."""

from __future__ import annotations

import uuid

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.roadmap import (
    Resource,
    RoadmapPhase,
    Topic,
    TopicChecklistItem,
    TopicNote,
    TopicProgress,
    TopicResource,
)


def list_phases(db: Session, track: str | None = None) -> list[RoadmapPhase]:
    stmt = select(RoadmapPhase).options(selectinload(RoadmapPhase.topics))
    if track is not None:
        stmt = stmt.where(RoadmapPhase.track == track)
    stmt = stmt.order_by(RoadmapPhase.order_index)
    return list(db.scalars(stmt).unique().all())


def get_phase(db: Session, phase_id: uuid.UUID) -> RoadmapPhase | None:
    return db.get(RoadmapPhase, phase_id)


def get_phase_by_key(db: Session, key: str) -> RoadmapPhase | None:
    return db.scalar(select(RoadmapPhase).where(RoadmapPhase.key == key))


def list_topics(db: Session, track: str | None = None) -> list[Topic]:
    stmt = (
        select(Topic)
        .options(
            selectinload(Topic.resource_links).selectinload(TopicResource.resource),
            selectinload(Topic.phase),
        )
        .join(RoadmapPhase, Topic.phase_id == RoadmapPhase.id)
        .order_by(RoadmapPhase.order_index, Topic.order_index)
    )
    if track is not None:
        stmt = stmt.where(RoadmapPhase.track == track)
    return list(db.scalars(stmt).unique().all())


def get_topic(db: Session, topic_id: uuid.UUID) -> Topic | None:
    stmt = (
        select(Topic)
        .options(
            selectinload(Topic.resource_links).selectinload(TopicResource.resource),
            selectinload(Topic.phase),
        )
        .where(Topic.id == topic_id)
    )
    return db.scalar(stmt)


def get_topic_by_slug(db: Session, slug: str) -> Topic | None:
    return db.scalar(select(Topic).where(Topic.slug == slug))


def list_progress_for_user(db: Session, user_id: uuid.UUID) -> list[TopicProgress]:
    return list(
        db.scalars(select(TopicProgress).where(TopicProgress.user_id == user_id)).all()
    )


def get_progress(db: Session, user_id: uuid.UUID, topic_id: uuid.UUID) -> TopicProgress | None:
    return db.scalar(
        select(TopicProgress).where(
            TopicProgress.user_id == user_id, TopicProgress.topic_id == topic_id
        )
    )


def ensure_progress(db: Session, user_id: uuid.UUID, topic_id: uuid.UUID) -> TopicProgress:
    progress = get_progress(db, user_id, topic_id)
    if progress is None:
        progress = TopicProgress(user_id=user_id, topic_id=topic_id)
        db.add(progress)
        db.flush()
    return progress


def progress_counts_by_topic(db: Session, user_id: uuid.UUID) -> dict[uuid.UUID, TopicProgress]:
    rows = list_progress_for_user(db, user_id)
    return {row.topic_id: row for row in rows}


def list_notes(db: Session, user_id: uuid.UUID, topic_id: uuid.UUID) -> list[TopicNote]:
    return list(
        db.scalars(
            select(TopicNote)
            .where(TopicNote.user_id == user_id, TopicNote.topic_id == topic_id)
            .order_by(TopicNote.created_at.desc())
        ).all()
    )


def create_note(db: Session, *, user_id: uuid.UUID, topic_id: uuid.UUID, content: str) -> TopicNote:
    note = TopicNote(user_id=user_id, topic_id=topic_id, content=content)
    db.add(note)
    db.flush()
    return note


def get_note(db: Session, user_id: uuid.UUID, note_id: uuid.UUID) -> TopicNote | None:
    return db.scalar(
        select(TopicNote).where(TopicNote.user_id == user_id, TopicNote.id == note_id)
    )


def list_checklist(db: Session, user_id: uuid.UUID, topic_id: uuid.UUID) -> list[TopicChecklistItem]:
    return list(
        db.scalars(
            select(TopicChecklistItem)
            .where(
                TopicChecklistItem.user_id == user_id,
                TopicChecklistItem.topic_id == topic_id,
            )
            .order_by(TopicChecklistItem.order_index, TopicChecklistItem.created_at)
        ).all()
    )


def create_checklist_item(
    db: Session, *, user_id: uuid.UUID, topic_id: uuid.UUID, title: str, is_done: bool = False
) -> TopicChecklistItem:
    existing = list_checklist(db, user_id, topic_id)
    order_index = len(existing)
    item = TopicChecklistItem(
        user_id=user_id, topic_id=topic_id, title=title, is_done=is_done, order_index=order_index
    )
    db.add(item)
    db.flush()
    return item


def get_checklist_item(
    db: Session, user_id: uuid.UUID, item_id: uuid.UUID
) -> TopicChecklistItem | None:
    return db.scalar(
        select(TopicChecklistItem).where(
            TopicChecklistItem.user_id == user_id, TopicChecklistItem.id == item_id
        )
    )


def list_resources(db: Session) -> list[Resource]:
    return list(db.scalars(select(Resource).order_by(Resource.category, Resource.title)).all())


def get_resource(db: Session, resource_id: uuid.UUID) -> Resource | None:
    return db.get(Resource, resource_id)


def count_topics(db: Session) -> int:
    return int(db.scalar(select(func.count()).select_from(Topic)) or 0)


def topic_progress_stmt(user_id: uuid.UUID) -> Select:
    return select(TopicProgress).where(TopicProgress.user_id == user_id)
