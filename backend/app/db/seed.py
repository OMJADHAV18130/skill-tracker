"""Idempotent seeding of shared roadmap data and per-user scaffolding."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.seed_data import PHASES, PROJECTS, RESOURCES, TOPIC_RESOURCE_MAP, TOPICS
from app.models import (
    DailyTask,
    Priority,
    Project,
    ProjectChecklistItem,
    ProjectMilestone,
    ProjectStatus,
    Resource,
    RoadmapPhase,
    StudySession,
    Topic,
    TopicChecklistItem,
    TopicNote,
    TopicProgress,
    TopicResource,
    TopicStatus,
    User,
    UserPreference,
)

logger = logging.getLogger("devpath.seed")


def _slugify(value: str) -> str:
    from slugify import slugify

    return slugify(value, max_length=150)


def seed_shared_roadmap(db: Session) -> dict[str, int]:
    """Insert the shared phases, topics, resources and links. Safe to re-run."""
    stats = {"phases": 0, "topics": 0, "resources": 0, "links": 0}

    # --- Phases ------------------------------------------------------------
    phase_by_key: dict[str, RoadmapPhase] = {}
    for order, data in enumerate(PHASES, start=1):
        phase = db.scalar(select(RoadmapPhase).where(RoadmapPhase.key == data["key"]))
        if phase is None:
            phase = RoadmapPhase(order_index=order, **data)
            db.add(phase)
            stats["phases"] += 1
        else:
            phase.title = data["title"]
            phase.summary = data["summary"]
            phase.month_label = data["month_label"]
            phase.duration_months = data["duration_months"]
            phase.project_brief = data["project_brief"]
            phase.accent = data["accent"]
            phase.track = data.get("track", "core")
            phase.order_index = order
        phase_by_key[data["key"]] = phase
    db.flush()

    # --- Topics ------------------------------------------------------------
    topic_by_slug: dict[str, Topic] = {}
    for phase_key, topics in TOPICS.items():
        phase = phase_by_key[phase_key]
        for index, (title, description, category, minutes, subtopics) in enumerate(topics):
            slug = _slugify(title)
            topic = db.scalar(select(Topic).where(Topic.slug == slug))
            if topic is None:
                topic = Topic(
                    slug=slug,
                    title=title,
                    description=description,
                    category=category,
                    estimated_minutes=minutes,
                    order_index=index + 1,
                    subtopics=list(subtopics),
                    is_key_topic=index == 0,
                    phase_id=phase.id,
                )
                db.add(topic)
                stats["topics"] += 1
            else:
                topic.phase_id = phase.id
                topic.title = title
                topic.description = description
                topic.category = category
                topic.estimated_minutes = minutes
                topic.order_index = index + 1
                topic.subtopics = list(subtopics)
            topic_by_slug[slug] = topic
    db.flush()

    # --- Resources ---------------------------------------------------------
    resource_by_title: dict[str, Resource] = {}
    for title, url, description, category, tags in RESOURCES:
        resource = db.scalar(select(Resource).where(Resource.title == title))
        if resource is None:
            resource = Resource(
                title=title,
                url=url,
                description=description,
                category=category,
                tags=list(tags),
                is_official=True,
            )
            db.add(resource)
            stats["resources"] += 1
        else:
            resource.url = url
            resource.description = description
            resource.category = category
            resource.tags = list(tags)
        resource_by_title[title] = resource
    db.flush()

    # --- Topic <-> Resource links -----------------------------------------
    existing_links = {
        (link.topic_id, link.resource_id) for link in db.scalars(select(TopicResource)).all()
    }
    for slug, resource_titles in TOPIC_RESOURCE_MAP.items():
        topic = topic_by_slug.get(slug)
        if topic is None:
            logger.warning("seed: topic slug %s not found, skipping link map", slug)
            continue
        for position, resource_title in enumerate(resource_titles):
            resource = resource_by_title.get(resource_title)
            if resource is None:
                continue
            if (topic.id, resource.id) in existing_links:
                continue
            db.add(
                TopicResource(
                    topic_id=topic.id,
                    resource_id=resource.id,
                    is_primary=position == 0,
                )
            )
            stats["links"] += 1

    # Every DSA topic gets the shared practice shelf: a guided roadmap, the
    # practice platform and the complexity reference.
    dsa_phase_ids = {phase.id for phase in phase_by_key.values() if phase.track == "dsa"}
    dsa_defaults = ["NeetCode Roadmap", "LeetCode", "Big-O Cheat Sheet"]
    for slug, topic in topic_by_slug.items():
        if topic.phase_id not in dsa_phase_ids or slug in TOPIC_RESOURCE_MAP:
            continue
        for position, resource_title in enumerate(dsa_defaults):
            resource = resource_by_title.get(resource_title)
            if resource is None:
                continue
            if (topic.id, resource.id) in existing_links:
                continue
            db.add(
                TopicResource(
                    topic_id=topic.id,
                    resource_id=resource.id,
                    is_primary=position == 0,
                )
            )
            stats["links"] += 1

    db.commit()
    return stats


def seed_user_content(db: Session, user: User) -> None:
    """Give a brand new user their own progress rows, preferences and projects."""
    _ensure_preferences(db, user)
    _ensure_topic_progress(db, user)
    _ensure_projects(db, user)


def _ensure_preferences(db: Session, user: User) -> UserPreference:
    pref = db.scalar(select(UserPreference).where(UserPreference.user_id == user.id))
    if pref is None:
        pref = UserPreference(user_id=user.id, roadmap_start_date=date.today())
        db.add(pref)
        db.flush()
    return pref


def _ensure_topic_progress(db: Session, user: User) -> int:
    """Create a progress row for every topic the user has not touched yet."""
    existing = {
        row.topic_id
        for row in db.scalars(
            select(TopicProgress).where(TopicProgress.user_id == user.id)
        ).all()
    }
    topics = db.scalars(select(Topic).order_by(Topic.order_index)).all()
    created = 0
    for topic in topics:
        if topic.id in existing:
            continue
        db.add(
            TopicProgress(
                user_id=user.id,
                topic_id=topic.id,
                status=TopicStatus.NOT_STARTED,
                priority=Priority.MEDIUM,
            )
        )
        created += 1
    if created:
        db.flush()
    return created


def _ensure_projects(db: Session, user: User) -> int:
    existing_names = {p.name for p in db.scalars(select(Project).where(Project.user_id == user.id)).all()}
    created = 0
    for order, template in enumerate(PROJECTS):
        if template["name"] in existing_names:
            continue
        project = Project(
            user_id=user.id,
            name=template["name"],
            description=template["description"],
            required_skills=list(template["required_skills"]),
            status=ProjectStatus.NOT_STARTED,
            priority=Priority.MEDIUM,
            order_index=order + 1,
        )
        db.add(project)
        db.flush()
        for index, (title, description) in enumerate(template["milestones"]):
            db.add(
                ProjectMilestone(
                    project_id=project.id,
                    title=title,
                    description=description,
                    order_index=index + 1,
                )
            )
        for index, title in enumerate(template["checklist"]):
            db.add(
                ProjectChecklistItem(
                    project_id=project.id, title=title, order_index=index + 1
                )
            )
        created += 1
    if created:
        db.flush()
    return created


def seed_demo_data(db: Session, user: User) -> dict[str, int]:
    """Populate the demo account with a believable few weeks of activity."""
    stats = {"tasks": 0, "sessions": 0, "progress": 0, "notes": 0, "checklist": 0}

    if db.scalar(select(DailyTask).where(DailyTask.user_id == user.id).limit(1)) is not None:
        return stats  # already seeded - keep it idempotent

    today = date.today()
    phase_order = [p["key"] for p in PHASES]

    # --- Progress: complete the first ~12 topics of phase 1 and part of 2 ---
    topics = db.scalars(
        select(Topic).order_by(Topic.phase_id, Topic.order_index)
    ).all()
    phase_rank = {key: index for index, key in enumerate(phase_order)}
    phase_ids = {
        p.key: p.id
        for p in db.scalars(select(RoadmapPhase)).all()
    }
    ordered = sorted(
        topics,
        key=lambda t: (
            phase_rank.get(_phase_key(phase_ids, t.phase_id), 99),
            t.order_index,
        ),
    )

    completed = 0
    for topic in ordered:
        if completed >= 12:
            break
        progress = db.scalar(
            select(TopicProgress).where(
                TopicProgress.user_id == user.id, TopicProgress.topic_id == topic.id
            )
        )
        if progress is None:
            continue
        status = TopicStatus.COMPLETED if completed < 9 else TopicStatus.IN_PROGRESS
        progress.status = status
        progress.started_at = datetime.now(UTC) - timedelta(days=30 - completed * 2)
        progress.rating = 4 if completed % 3 else 5
        if status is TopicStatus.COMPLETED:
            progress.completed_at = progress.started_at + timedelta(days=1)
            completed += 1
        stats["progress"] += 1

        if completed <= 3:
            db.add(
                TopicNote(
                    user_id=user.id,
                    topic_id=topic.id,
                    content=(
                        f"Key takeaway from {topic.title}: write the code twice - once to "
                        "understand it, once to make it clean."
                    ),
                )
            )
            stats["notes"] += 1
            for index, sub in enumerate(topic.subtopics[:3]):
                db.add(
                    TopicChecklistItem(
                        user_id=user.id,
                        topic_id=topic.id,
                        title=sub,
                        is_done=index < 2,
                        order_index=index,
                    )
                )
                stats["checklist"] += 1

    # --- Daily tasks for the last 10 days ---------------------------------
    task_titles = [
        ("Read Spring Data JPA reference (chapters 1-3)", "Spring Boot", 60, Priority.HIGH),
        ("Implement Repository layer for transactions", "Spring Boot", 90, Priority.HIGH),
        ("PostgreSQL indexing practice", "Databases", 45, Priority.MEDIUM),
        ("Solve 3 array problems on LeetCode", "DSA", 60, Priority.MEDIUM),
        ("Docker basics: images and layers", "Docker", 40, Priority.LOW),
        ("Git rebase practice", "CI/CD", 30, Priority.LOW),
        ("Write integration test with Testcontainers", "Java", 75, Priority.HIGH),
        ("Review Spring Security filter chain", "Security", 45, Priority.MEDIUM),
    ]
    for offset in range(-9, 1):
        day = today + timedelta(days=offset)
        for slot, (title, category, minutes, priority) in enumerate(task_titles[: 3 + (offset % 3)]):
            done = offset < 0 or (offset == 0 and slot == 0)
            task = DailyTask(
                user_id=user.id,
                title=title,
                task_date=day,
                category=category,
                estimated_minutes=minutes,
                actual_minutes=minutes if done else 0,
                priority=priority,
                is_completed=done,
                completed_at=datetime.now(UTC) - timedelta(days=-offset) if done else None,
                session_note="Focused session, no distractions." if done else None,
                order_index=slot,
            )
            db.add(task)
            db.flush()
            stats["tasks"] += 1
            if done:
                db.add(
                    StudySession(
                        user_id=user.id,
                        task_id=task.id,
                        session_date=day,
                        minutes=minutes,
                        note="Focused session, no distractions.",
                    )
                )
                stats["sessions"] += 1

    # --- A couple of project milestones completed --------------------------
    project = db.scalar(
        select(Project).where(Project.user_id == user.id).order_by(Project.order_index).limit(1)
    )
    if project is not None:
        milestones = db.scalars(
            select(ProjectMilestone)
            .where(ProjectMilestone.project_id == project.id)
            .order_by(ProjectMilestone.order_index)
        ).all()
        for milestone in milestones[:2]:
            milestone.is_completed = True
            milestone.completed_at = datetime.now(UTC)
        project.status = ProjectStatus.IN_PROGRESS
        project.start_date = today - timedelta(days=21)
        project.target_date = today + timedelta(days=21)
        project.repo_url = "https://github.com/demo/java-expense-tracker"
        project.notes = "Started with the CLI and JDBC layer - going well."

    db.commit()
    return stats


def _phase_key(phase_ids: dict[str, object], phase_id: object) -> str:
    for key, pid in phase_ids.items():
        if pid == phase_id:
            return key
    return ""


def ensure_demo_user(db: Session) -> User | None:
    """Create (or fetch) the documented local demo account."""
    email = settings.demo_user_email.lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(
            email=email,
            username=settings.demo_user_username,
            full_name=settings.demo_user_full_name,
            hashed_password=hash_password(settings.demo_user_password),
        )
        db.add(user)
        db.flush()
        logger.info("Created demo user %s", email)
    seed_user_content(db, user)
    db.commit()
    return user


def run_full_seed(db: Session, *, include_demo: bool = True) -> dict[str, object]:
    shared = seed_shared_roadmap(db)
    result: dict[str, object] = {"shared": shared, "demo": None}
    if include_demo:
        demo = ensure_demo_user(db)
        if demo is not None:
            demo_stats = seed_demo_data(db, demo)
            result["demo"] = demo_stats
    return result


def main() -> None:  # pragma: no cover - CLI helper
    """`python -m app.db.seed [--no-demo]`"""
    import argparse

    from app.core.logging_config import configure_logging
    from app.db.session import SessionLocal

    parser = argparse.ArgumentParser(description="Seed DevPath shared and demo data")
    parser.add_argument("--no-demo", action="store_true", help="Skip the demo account")
    args = parser.parse_args()

    configure_logging()
    with SessionLocal() as db:
        result = run_full_seed(db, include_demo=not args.no_demo)
    logger.info("Seed result: %s", result)
    print(result)


if __name__ == "__main__":
    main()
