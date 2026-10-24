"""Dashboard aggregation - every figure is derived from persisted rows."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.planner import StudySession
from app.models.preference import UserPreference
from app.models.project import Project, ProjectMilestone
from app.models.roadmap import TopicProgress, TopicStatus
from app.repositories import planner_repo, preference_repo, project_repo, roadmap_repo
from app.schemas.dashboard import (
    ActivityDto,
    DailyStudyPoint,
    DailyTaskDto,
    DashboardRead,
    DsaTrackDto,
    MilestoneDto,
    PhaseProgressDto,
    ProjectStatusDto,
)
from app.services import progress_service, roadmap_service
from app.services.preference_service import sync_dsa_pause


def _week_start(reference: date) -> date:
    return reference - timedelta(days=reference.weekday())


def build_dashboard(db: Session, user_id: uuid.UUID) -> DashboardRead:
    phases = roadmap_repo.list_phases(db)
    topics = roadmap_repo.list_topics(db)
    progress_by_topic = roadmap_repo.progress_counts_by_topic(db, user_id)

    core_phases = [phase for phase in phases if getattr(phase, "track", "core") == "core"]
    core_topics = [topic for topic in topics if getattr(topic.phase, "track", "core") == "core"]
    dsa_phases = [phase for phase in phases if getattr(phase, "track", "core") == "dsa"]
    dsa_topics = [topic for topic in topics if getattr(topic.phase, "track", "core") == "dsa"]

    stats = progress_service.build_roadmap_stats(
        phases=core_phases, topics=core_topics, progress_by_topic=progress_by_topic
    )

    # --- current phase ------------------------------------------------------
    current_phase: dict = {}
    phase_for_topic: dict = {}
    for phase in phases:
        for topic in topics:
            if topic.phase_id == phase.id:
                phase_for_topic.setdefault(phase.key, []).append(topic)

    active_phase = None
    for phase_stats in stats.phases:
        if phase_stats.status == "in_progress":
            active_phase = phase_stats
            break
    if active_phase is None:
        for phase_stats in stats.phases:
            if phase_stats.status != "completed":
                active_phase = phase_stats
                break
    if active_phase is None and stats.phases:
        active_phase = stats.phases[-1]

    if active_phase is not None:
        phase_row = next((p for p in phases if p.key == active_phase.key), None)
        current_phase = {
            "key": active_phase.key,
            "title": active_phase.title,
            "month_label": active_phase.month_label,
            "completion_percentage": active_phase.completion_percentage,
            "completed_topics": active_phase.completed_topics,
            "total_topics": active_phase.total_topics,
            "project_brief": phase_row.project_brief if phase_row else None,
        }

    # --- next recommended topic --------------------------------------------
    recommended = roadmap_service.next_recommended_topic(db, user_id)
    next_recommended: dict = {}
    if recommended is not None:
        next_recommended = {
            "id": str(recommended.id),
            "title": recommended.title,
            "description": recommended.description,
            "category": recommended.category,
            "estimated_minutes": recommended.estimated_minutes,
            "status": recommended.progress.status.value,
            "phase_id": str(recommended.phase_id),
        }

    # --- study time + streak ------------------------------------------------
    total_minutes = planner_repo.total_minutes(db, user_id)
    streak = progress_service.compute_streak(planner_repo.active_dates(db, user_id))

    goal = 120
    from app.repositories import preference_repo

    pref = preference_repo.get_or_create_preference(db, user_id)
    goal = pref.daily_goal_minutes

    today = date.today()
    week_start = _week_start(today)
    minutes_by_day = planner_repo.minutes_by_date(db, user_id, start=week_start, end=today)
    weekly_study: list[DailyStudyPoint] = []
    for offset in range(7):
        day = week_start + timedelta(days=offset)
        weekly_study.append(
            DailyStudyPoint(
                date=day,
                minutes=minutes_by_day.get(day, 0),
                goal_minutes=goal,
                label=day.strftime("%a"),
            )
        )

    # --- today's tasks ------------------------------------------------------
    today_tasks = planner_repo.list_tasks(db, user_id, start=today, end=today, limit=200)
    todays_tasks = [
        DailyTaskDto(
            id=task.id,
            title=task.title,
            task_date=task.task_date,
            category=task.category,
            estimated_minutes=task.estimated_minutes,
            priority=task.priority.value,
            is_completed=task.is_completed,
        )
        for task in today_tasks
    ]
    planned_minutes = sum(t.estimated_minutes for t in today_tasks)
    completed_minutes = sum(t.actual_minutes for t in today_tasks if t.is_completed)
    logged_today = sum(
        s.minutes for s in planner_repo.list_sessions(db, user_id, start=today, end=today)
    )

    # --- phase chart --------------------------------------------------------
    phase_progress = [
        PhaseProgressDto(
            key=phase.key,
            title=phase.title,
            month_label=phase.month_label,
            completion_percentage=phase.completion_percentage,
            completed_topics=phase.completed_topics,
            total_topics=phase.total_topics,
            status=phase.status,
        )
        for phase in stats.phases
    ]

    # --- projects -----------------------------------------------------------
    projects = project_repo.list_projects(db, user_id)
    project_dtos: list[ProjectStatusDto] = []
    projects_completed = 0
    for project in projects:
        milestones = list(project.milestones or [])
        completed_milestones = sum(1 for m in milestones if m.is_completed)
        percentage = round(completed_milestones / len(milestones) * 100, 2) if milestones else 0.0
        if project.status.value == "completed":
            projects_completed += 1
        project_dtos.append(
            ProjectStatusDto(
                id=project.id,
                name=project.name,
                status=project.status.value,
                completion_percentage=percentage,
                completed_milestones=completed_milestones,
                milestone_count=len(milestones),
                repo_url=project.repo_url,
                demo_url=project.demo_url,
            )
        )

    # --- upcoming milestones ------------------------------------------------
    upcoming: list[MilestoneDto] = []
    for project in projects:
        for milestone in project.milestones or []:
            if milestone.is_completed:
                continue
            due = milestone.due_date or project.target_date
            upcoming.append(
                MilestoneDto(
                    id=str(milestone.id),
                    title=milestone.title,
                    kind="project",
                    due_label=due.isoformat() if due else None,
                    completed=False,
                    subtitle=project.name,
                )
            )
    upcoming.sort(key=lambda m: (m.due_label is None, m.due_label or ""))
    upcoming = upcoming[:6]

    # --- recent activity ----------------------------------------------------
    activity: list[ActivityDto] = []
    recent_progress = db.scalars(
        select(TopicProgress)
        .where(TopicProgress.user_id == user_id)
        .order_by(TopicProgress.updated_at.desc())
        .limit(20)
    ).all()
    topic_map = {t.id: t for t in topics}
    for row in recent_progress:
        if row.status == TopicStatus.NOT_STARTED:
            continue
        topic = topic_map.get(row.topic_id)
        activity.append(
            ActivityDto(
                id=str(row.id),
                type="topic_completed" if row.status == TopicStatus.COMPLETED else "topic_started",
                title=topic.title if topic else "Topic",
                detail=(
                    "Completed" if row.status == TopicStatus.COMPLETED else "In progress"
                ),
                occurred_at=row.updated_at.isoformat() if row.updated_at else None,
            )
        )

    recent_sessions = db.scalars(
        select(StudySession)
        .where(StudySession.user_id == user_id)
        .order_by(StudySession.created_at.desc())
        .limit(10)
    ).all()
    for session in recent_sessions:
        activity.append(
            ActivityDto(
                id=str(session.id),
                type="study_session",
                title=f"{session.minutes} min study session",
                detail=session.note,
                occurred_at=session.created_at.isoformat() if session.created_at else None,
            )
        )

    recent_milestones = db.scalars(
        select(ProjectMilestone)
        .join(Project, ProjectMilestone.project_id == Project.id)
        .where(Project.user_id == user_id, ProjectMilestone.is_completed.is_(True))
        .order_by(ProjectMilestone.completed_at.desc())
        .limit(10)
    ).all()
    project_map = {p.id: p for p in projects}
    for milestone in recent_milestones:
        project = project_map.get(milestone.project_id)
        activity.append(
            ActivityDto(
                id=str(milestone.id),
                type="milestone_completed",
                title=milestone.title,
                detail=project.name if project else None,
                occurred_at=milestone.completed_at.isoformat()
                if milestone.completed_at
                else None,
            )
        )

    activity.sort(key=lambda item: item.occurred_at or "", reverse=True)
    activity = activity[:10]

    dsa_stats = progress_service.build_roadmap_stats(
        phases=dsa_phases, topics=dsa_topics, progress_by_topic=progress_by_topic
    )
    dsa_phases_dto = [
        PhaseProgressDto(
            key=phase.key,
            title=phase.title,
            month_label=phase.month_label,
            completion_percentage=phase.completion_percentage,
            completed_topics=phase.completed_topics,
            total_topics=phase.total_topics,
            status=phase.status,
        )
        for phase in dsa_stats.phases
    ]
    dsa_next: dict = {}
    if not pref.dsa_paused:
        try:
            next_dsa = roadmap_service.next_recommended_topic(db, user_id, track="dsa")
            if next_dsa is not None:
                dsa_next = {
                    "id": str(next_dsa.id),
                    "title": next_dsa.title,
                    "description": next_dsa.description,
                    "category": next_dsa.category,
                    "estimated_minutes": next_dsa.estimated_minutes,
                    "status": next_dsa.progress.status.value,
                    "phase_id": str(next_dsa.phase_id),
                }
        except Exception:
            dsa_next = {}
    else:
        dsa_next = {}

    dsa_summary = DsaTrackDto(
        total_topics=dsa_stats.total_topics,
        completed_topics=dsa_stats.completed_topics,
        in_progress_topics=dsa_stats.in_progress_topics,
        completion_percentage=dsa_stats.completion_percentage,
        paused=pref.dsa_paused,
        paused_until=pref.dsa_paused_until,
        phases=dsa_phases_dto,
        next_recommended_topic=dsa_next,
    )

    return DashboardRead(
        overall_completion_percentage=stats.completion_percentage,
        completed_topics=stats.completed_topics,
        total_topics=stats.total_topics,
        in_progress_topics=stats.in_progress_topics,
        current_phase=current_phase,
    next_recommended_topic=next_recommended,
    dsa=dsa_summary,
    total_study_minutes=total_minutes,
        total_study_hours=round(total_minutes / 60, 2),
        current_streak=streak.current_streak,
        longest_streak=streak.longest_streak,
        weekly_study=weekly_study,
        phase_progress=phase_progress,
        todays_tasks=todays_tasks,
        todays_planned_minutes=planned_minutes,
        todays_completed_minutes=completed_minutes,
        todays_goal_minutes=goal,
        todays_goal_percentage=round((logged_today / goal * 100), 2) if goal else 0.0,
        upcoming_milestones=upcoming,
        recent_activity=activity,
        projects=project_dtos,
        projects_completed=projects_completed,
        projects_total=len(projects),
    )
