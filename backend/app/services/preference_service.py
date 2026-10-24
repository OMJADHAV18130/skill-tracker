"""User preferences, data export, import and reset."""

from __future__ import annotations

import csv
import io
import uuid
from datetime import UTC, date, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.errors import ValidationError
from app.models.planner import DailyTask, StudySession
from app.models.project import Project, ProjectChecklistItem, ProjectMilestone
from app.models.resource import UserResourceLink
from app.models.roadmap import TopicChecklistItem, TopicNote, TopicProgress
from app.repositories import preference_repo
from app.schemas.preference import ExportPayload, ImportPreview, PreferenceRead, PreferenceUpdate


def get_preferences(db: Session, user_id: uuid.UUID) -> PreferenceRead:
    pref = preference_repo.get_or_create_preference(db, user_id)
    sync_dsa_pause(pref)
    db.commit()
    db.refresh(pref)
    return PreferenceRead.model_validate(pref)


def sync_dsa_pause(pref) -> bool:
    """Auto-resume the DSA track once its pause window has elapsed."""
    if (
        pref.dsa_paused
        and pref.dsa_paused_until is not None
        and pref.dsa_paused_until <= date.today()
    ):
        pref.dsa_paused = False
        pref.dsa_paused_at = None
        pref.dsa_paused_until = None
        return True
    return False


def pause_dsa(db: Session, user_id: uuid.UUID, resume_on: date | None) -> PreferenceRead:
    pref = preference_repo.get_or_create_preference(db, user_id)
    if resume_on is not None and resume_on <= date.today():
        raise ValidationError(
            "The resume date must be in the future", code="invalid_resume_date"
        )
    pref.dsa_paused = True
    pref.dsa_paused_at = datetime.now(UTC)
    pref.dsa_paused_until = resume_on
    db.commit()
    db.refresh(pref)
    return PreferenceRead.model_validate(pref)


def resume_dsa(db: Session, user_id: uuid.UUID) -> PreferenceRead:
    pref = preference_repo.get_or_create_preference(db, user_id)
    pref.dsa_paused = False
    pref.dsa_paused_at = None
    pref.dsa_paused_until = None
    db.commit()
    db.refresh(pref)
    return PreferenceRead.model_validate(pref)


def update_preferences(
    db: Session, user_id: uuid.UUID, payload: PreferenceUpdate
) -> PreferenceRead:
    pref = preference_repo.get_or_create_preference(db, user_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "phase_durations" and value is not None:
            merged = dict(pref.phase_durations or {})
            merged.update({k: int(v) for k, v in value.items()})
            pref.phase_durations = merged
            continue
        setattr(pref, field, value)
    db.commit()
    db.refresh(pref)
    return PreferenceRead.model_validate(pref)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
def build_export(db: Session, user_id: uuid.UUID) -> ExportPayload:
    from app.repositories import roadmap_repo, user_repo

    user = user_repo.get_by_id(db, user_id)
    pref = preference_repo.get_or_create_preference(db, user_id)
    topics = {t.id: t for t in roadmap_repo.list_topics(db)}
    progress_rows = db.scalars(
        select(TopicProgress).where(TopicProgress.user_id == user_id)
    ).all()

    topic_progress = [
        {
            "topic_id": str(row.topic_id),
            "slug": topics[row.topic_id].slug if row.topic_id in topics else None,
            "title": topics[row.topic_id].title if row.topic_id in topics else None,
            "status": row.status.value,
            "priority": row.priority.value,
            "rating": row.rating,
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "completed_at": row.completed_at.isoformat() if row.completed_at else None,
        }
        for row in progress_rows
    ]

    notes = [
        {
            "topic_id": str(row.topic_id),
            "content": row.content,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in db.scalars(select(TopicNote).where(TopicNote.user_id == user_id)).all()
    ]

    checklist = [
        {
            "topic_id": str(row.topic_id),
            "title": row.title,
            "is_done": row.is_done,
            "order_index": row.order_index,
        }
        for row in db.scalars(
            select(TopicChecklistItem).where(TopicChecklistItem.user_id == user_id)
        ).all()
    ]

    tasks = [
        {
            "title": row.title,
            "description": row.description,
            "task_date": row.task_date.isoformat(),
            "category": row.category,
            "estimated_minutes": row.estimated_minutes,
            "actual_minutes": row.actual_minutes,
            "priority": row.priority.value,
            "is_completed": row.is_completed,
            "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            "session_note": row.session_note,
            "topic_id": str(row.topic_id) if row.topic_id else None,
        }
        for row in db.scalars(select(DailyTask).where(DailyTask.user_id == user_id)).all()
    ]

    sessions = [
        {
            "minutes": row.minutes,
            "session_date": row.session_date.isoformat(),
            "note": row.note,
            "topic_id": str(row.topic_id) if row.topic_id else None,
        }
        for row in db.scalars(select(StudySession).where(StudySession.user_id == user_id)).all()
    ]

    projects = db.scalars(select(Project).where(Project.user_id == user_id)).all()
    milestones = []
    checklist_projects = []
    for project in projects:
        milestones.extend(
            {
                "project": project.name,
                "title": m.title,
                "description": m.description,
                "is_completed": m.is_completed,
                "due_date": m.due_date.isoformat() if m.due_date else None,
                "order_index": m.order_index,
            }
            for m in db.scalars(
                select(ProjectMilestone).where(ProjectMilestone.project_id == project.id)
            ).all()
        )
        checklist_projects.extend(
            {
                "project": project.name,
                "title": c.title,
                "is_done": c.is_done,
                "order_index": c.order_index,
            }
            for c in db.scalars(
                select(ProjectChecklistItem).where(ProjectChecklistItem.project_id == project.id)
            ).all()
        )

    bookmarks = [
        {
            "resource_id": str(row.resource_id),
            "is_bookmarked": row.is_bookmarked,
            "linked_topic_id": str(row.linked_topic_id) if row.linked_topic_id else None,
            "notes": row.notes,
        }
        for row in db.scalars(select(UserResourceLink).where(UserResourceLink.user_id == user_id)).all()
    ]

    return ExportPayload(
        exported_at=datetime.now(UTC),
        user={
            "email": user.email if user else None,
            "username": user.username if user else None,
            "full_name": user.full_name if user else None,
        },
        preferences={
            "daily_goal_minutes": pref.daily_goal_minutes,
            "roadmap_start_date": pref.roadmap_start_date.isoformat(),
            "theme": pref.theme.value,
            "reminders_enabled": pref.reminders_enabled,
            "reminder_time": pref.reminder_time.isoformat(),
            "timezone": pref.timezone,
            "phase_durations": dict(pref.phase_durations or {}),
            "dsa_paused": pref.dsa_paused,
            "dsa_paused_at": pref.dsa_paused_at.isoformat() if pref.dsa_paused_at else None,
            "dsa_paused_until": (
                pref.dsa_paused_until.isoformat() if pref.dsa_paused_until else None
            ),
        },
        topic_progress=topic_progress,
        topic_notes=notes,
        topic_checklist=checklist,
        daily_tasks=tasks,
        study_sessions=sessions,
        projects=[
            {
                "name": p.name,
                "description": p.description,
                "required_skills": list(p.required_skills or []),
                "status": p.status.value,
                "priority": p.priority.value,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "target_date": p.target_date.isoformat() if p.target_date else None,
                "repo_url": p.repo_url,
                "demo_url": p.demo_url,
                "notes": p.notes,
                "order_index": p.order_index,
            }
            for p in projects
        ],
        project_milestones=milestones,
        project_checklist=checklist_projects,
        resource_bookmarks=bookmarks,
    )


def export_csv(db: Session, user_id: uuid.UUID) -> str:
    """Flat CSV of every completed/started topic with its study minutes."""
    export = build_export(db, user_id)
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        [
            "topic_slug",
            "topic_title",
            "status",
            "priority",
            "rating",
            "started_at",
            "completed_at",
            "notes_count",
        ]
    )
    notes_by_topic: dict[str, int] = {}
    for note in export.topic_notes:
        notes_by_topic[note["topic_id"]] = notes_by_topic.get(note["topic_id"], 0) + 1
    for row in export.topic_progress:
        writer.writerow(
            [
                row["slug"] or "",
                row["title"] or "",
                row["status"],
                row["priority"],
                row["rating"] if row["rating"] is not None else "",
                row["started_at"] or "",
                row["completed_at"] or "",
                notes_by_topic.get(row["topic_id"], 0),
            ]
        )
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------
def validate_export(payload: ExportPayload) -> ImportPreview:
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, int] = {
        "topic_progress": len(payload.topic_progress),
        "topic_notes": len(payload.topic_notes),
        "topic_checklist": len(payload.topic_checklist),
        "daily_tasks": len(payload.daily_tasks),
        "study_sessions": len(payload.study_sessions),
        "projects": len(payload.projects),
        "project_milestones": len(payload.project_milestones),
        "project_checklist": len(payload.project_checklist),
        "resource_bookmarks": len(payload.resource_bookmarks),
    }

    if not payload.schema_version:
        errors.append("Missing schema_version")
    elif payload.schema_version.split(".")[0] != "1":
        errors.append(f"Unsupported schema version: {payload.schema_version}")

    for index, task in enumerate(payload.daily_tasks):
        if not task.get("title"):
            errors.append(f"daily_tasks[{index}] is missing a title")
        if not task.get("task_date"):
            errors.append(f"daily_tasks[{index}] is missing a date")

    for index, session in enumerate(payload.study_sessions):
        minutes = session.get("minutes")
        if not isinstance(minutes, int) or minutes <= 0:
            errors.append(f"study_sessions[{index}] has an invalid duration")

    for index, row in enumerate(payload.topic_progress):
        if row.get("status") not in {"not_started", "in_progress", "completed"}:
            errors.append(f"topic_progress[{index}] has an invalid status")

    if payload.preferences:
        goal = payload.preferences.get("daily_goal_minutes")
        if goal is not None and not (30 <= int(goal) <= 480):
            warnings.append("Daily goal outside the supported 30-480 minute range, clamping")

    return ImportPreview(
        valid=not errors,
        schema_version=payload.schema_version,
        warnings=warnings,
        errors=errors,
        counts=counts,
    )


def import_export(
    db: Session, user_id: uuid.UUID, payload: ExportPayload, *, mode: str = "replace"
) -> dict[str, int]:
    from app.repositories import roadmap_repo, user_repo

    preview = validate_export(payload)
    if not preview.valid:
        raise ValidationError(
            "The import file is not valid", code="invalid_import", details={"errors": preview.errors}
        )

    user_repo.get_by_id(db, user_id)
    topics = {t.slug: t for t in roadmap_repo.list_topics(db)}
    topics_by_id = {t.id: t for t in topics.values()}

    if mode == "replace":
        for model in (
            TopicNote,
            TopicChecklistItem,
            DailyTask,
            StudySession,
            TopicProgress,
        ):
            db.execute(delete(model).where(model.user_id == user_id))
        for project in db.scalars(select(Project).where(Project.user_id == user_id)).all():
            db.execute(
                delete(ProjectMilestone).where(ProjectMilestone.project_id == project.id)
            )
            db.execute(
                delete(ProjectChecklistItem).where(ProjectChecklistItem.project_id == project.id)
            )
        db.execute(delete(Project).where(Project.user_id == user_id))
        db.execute(delete(UserResourceLink).where(UserResourceLink.user_id == user_id))
        db.flush()

    # --- preferences --------------------------------------------------------
    pref = preference_repo.get_or_create_preference(db, user_id)
    raw_prefs = payload.preferences or {}
    if raw_prefs.get("daily_goal_minutes"):
        pref.daily_goal_minutes = max(30, min(480, int(raw_prefs["daily_goal_minutes"])))
    if raw_prefs.get("roadmap_start_date"):
        from datetime import date as _date

        try:
            pref.roadmap_start_date = _date.fromisoformat(raw_prefs["roadmap_start_date"])
        except ValueError:
            pass
    if raw_prefs.get("theme"):
        from app.models.preference import Theme

        try:
            pref.theme = Theme(raw_prefs["theme"])
        except ValueError:
            pass
    if raw_prefs.get("timezone"):
        pref.timezone = str(raw_prefs["timezone"])
    if raw_prefs.get("phase_durations"):
        merged = dict(pref.phase_durations or {})
        merged.update({k: int(v) for k, v in raw_prefs["phase_durations"].items()})
        pref.phase_durations = merged
    if "dsa_paused" in raw_prefs:
        pref.dsa_paused = bool(raw_prefs["dsa_paused"])
        pref.dsa_paused_at = _parse_dt(raw_prefs.get("dsa_paused_at"))
        pref.dsa_paused_until = _parse_date(raw_prefs.get("dsa_paused_until"))
        sync_dsa_pause(pref)

    counters = {
        "topic_progress": 0,
        "topic_notes": 0,
        "topic_checklist": 0,
        "daily_tasks": 0,
        "study_sessions": 0,
        "projects": 0,
        "project_milestones": 0,
        "project_checklist": 0,
        "resource_bookmarks": 0,
    }

    # --- topic progress -----------------------------------------------------
    for row in payload.topic_progress:
        topic = None
        if row.get("topic_id") in topics_by_id:
            topic = topics_by_id[row["topic_id"]]
        elif row.get("slug"):
            topic = topics.get(row["slug"])
        if topic is None:
            continue
        existing = db.scalar(
            select(TopicProgress).where(
                TopicProgress.user_id == user_id, TopicProgress.topic_id == topic.id
            )
        )
        if existing is None:
            existing = TopicProgress(user_id=user_id, topic_id=topic.id)
            db.add(existing)
        existing.status = row.get("status", "not_started")
        existing.priority = row.get("priority", "medium")
        existing.rating = row.get("rating")
        existing.started_at = _parse_dt(row.get("started_at"))
        existing.completed_at = _parse_dt(row.get("completed_at"))
        counters["topic_progress"] += 1

    # --- notes / checklist --------------------------------------------------
    for note in payload.topic_notes:
        topic = topics_by_id.get(note.get("topic_id"))
        if topic is None:
            continue
        db.add(TopicNote(user_id=user_id, topic_id=topic.id, content=note.get("content", "")))
        counters["topic_notes"] += 1

    for item in payload.topic_checklist:
        topic = topics_by_id.get(item.get("topic_id"))
        if topic is None:
            continue
        db.add(
            TopicChecklistItem(
                user_id=user_id,
                topic_id=topic.id,
                title=item.get("title", ""),
                is_done=bool(item.get("is_done")),
                order_index=int(item.get("order_index", 0)),
            )
        )
        counters["topic_checklist"] += 1

    # --- tasks / sessions ---------------------------------------------------
    from datetime import date as _date

    task_map: dict[str, uuid.UUID] = {}
    for task in payload.daily_tasks:
        try:
            task_date = _date.fromisoformat(task["task_date"])
        except (KeyError, ValueError):
            continue
        row = DailyTask(
            user_id=user_id,
            title=task.get("title", "Untitled"),
            description=task.get("description"),
            task_date=task_date,
            category=task.get("category", "General"),
            estimated_minutes=int(task.get("estimated_minutes", 0)),
            actual_minutes=int(task.get("actual_minutes", 0)),
            priority=task.get("priority", "medium"),
            is_completed=bool(task.get("is_completed")),
            completed_at=_parse_dt(task.get("completed_at")),
            session_note=task.get("session_note"),
            order_index=len(task_map),
        )
        db.add(row)
        db.flush()
        task_map[str(row.id)] = row.id
        counters["daily_tasks"] += 1

    for session in payload.study_sessions:
        try:
            session_date = _date.fromisoformat(session["session_date"])
        except (KeyError, ValueError):
            continue
        minutes = int(session.get("minutes", 0))
        if minutes <= 0:
            continue
        db.add(
            StudySession(
                user_id=user_id,
                session_date=session_date,
                minutes=minutes,
                note=session.get("note"),
                created_at=datetime.now(UTC),
            )
        )
        counters["study_sessions"] += 1

    # --- projects -----------------------------------------------------------
    existing_projects = {
        p.name: p for p in db.scalars(select(Project).where(Project.user_id == user_id)).all()
    }
    for order, project_data in enumerate(payload.projects):
        name = project_data.get("name")
        if not name:
            continue
        project = existing_projects.get(name)
        if project is None:
            project = Project(
                user_id=user_id,
                name=name,
                description=project_data.get("description", ""),
                required_skills=list(project_data.get("required_skills") or []),
                status=project_data.get("status", "not_started"),
                priority=project_data.get("priority", "medium"),
                start_date=_parse_date(project_data.get("start_date")),
                target_date=_parse_date(project_data.get("target_date")),
                repo_url=project_data.get("repo_url"),
                demo_url=project_data.get("demo_url"),
                notes=project_data.get("notes"),
                order_index=int(project_data.get("order_index", order)),
            )
            db.add(project)
            db.flush()
            counters["projects"] += 1

    project_by_name = {
        p.name: p for p in db.scalars(select(Project).where(Project.user_id == user_id)).all()
    }
    for milestone in payload.project_milestones:
        project = project_by_name.get(milestone.get("project"))
        if project is None:
            continue
        db.add(
            ProjectMilestone(
                project_id=project.id,
                title=milestone.get("title", ""),
                description=milestone.get("description"),
                is_completed=bool(milestone.get("is_completed")),
                due_date=_parse_date(milestone.get("due_date")),
                order_index=int(milestone.get("order_index", 0)),
            )
        )
        counters["project_milestones"] += 1

    for item in payload.project_checklist:
        project = project_by_name.get(item.get("project"))
        if project is None:
            continue
        db.add(
            ProjectChecklistItem(
                project_id=project.id,
                title=item.get("title", ""),
                is_done=bool(item.get("is_done")),
                order_index=int(item.get("order_index", 0)),
            )
        )
        counters["project_checklist"] += 1

    # --- bookmarks ----------------------------------------------------------
    for bookmark in payload.resource_bookmarks:
        resource_id = bookmark.get("resource_id")
        if not resource_id:
            continue
        db.add(
            UserResourceLink(
                user_id=user_id,
                resource_id=uuid.UUID(resource_id),
                linked_topic_id=uuid.UUID(bookmark["linked_topic_id"])
                if bookmark.get("linked_topic_id")
                else None,
                is_bookmarked=bool(bookmark.get("is_bookmarked")),
                notes=bookmark.get("notes"),
            )
        )
        counters["resource_bookmarks"] += 1

    db.commit()
    return counters


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _parse_date(value):
    if not value:
        return None
    try:
        from datetime import date as _date

        return _date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------
def reset_progress(db: Session, user_id: uuid.UUID) -> dict[str, int]:
    """Wipe every personal progress record and re-seed the default projects."""
    from app.db.seed import seed_user_content
    from app.repositories import user_repo

    counters = {}
    for model, key in (
        (TopicNote, "topic_notes"),
        (TopicChecklistItem, "topic_checklist"),
        (DailyTask, "daily_tasks"),
        (StudySession, "study_sessions"),
        (TopicProgress, "topic_progress"),
    ):
        result = db.execute(delete(model).where(model.user_id == user_id))
        counters[key] = int(result.rowcount or 0)

    for project in db.scalars(select(Project).where(Project.user_id == user_id)).all():
        db.execute(delete(ProjectMilestone).where(ProjectMilestone.project_id == project.id))
        db.execute(delete(ProjectChecklistItem).where(ProjectChecklistItem.project_id == project.id))
    result = db.execute(delete(Project).where(Project.user_id == user_id))
    counters["projects"] = int(result.rowcount or 0)
    db.execute(delete(UserResourceLink).where(UserResourceLink.user_id == user_id))
    db.flush()

    pref = preference_repo.get_or_create_preference(db, user_id)
    pref.phase_durations = {}
    pref.dsa_paused = False
    pref.dsa_paused_at = None
    pref.dsa_paused_until = None
    db.flush()

    seed_user_content(db, user_repo.get_by_id(db, user_id))
    db.commit()
    return counters
