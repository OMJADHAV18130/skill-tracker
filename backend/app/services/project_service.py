"""Project tracker service."""

from __future__ import annotations

import uuid
from datetime import UTC, date

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.project import ProjectStatus
from app.repositories import project_repo
from app.schemas.project import (
    ProjectChecklistItemCreate,
    ProjectChecklistItemRead,
    ProjectChecklistItemUpdate,
    ProjectCreate,
    ProjectMilestoneCreate,
    ProjectMilestoneRead,
    ProjectMilestoneUpdate,
    ProjectRead,
    ProjectSummary,
    ProjectUpdate,
)


def _read(project) -> ProjectRead:
    milestones = list(project.milestones or [])
    checklist_items = list(project.checklist_items or [])
    completed_milestones = sum(1 for m in milestones if m.is_completed)
    completed_checklist = sum(1 for c in checklist_items if c.is_done)

    days_remaining = None
    if project.target_date is not None:
        days_remaining = (project.target_date - date.today()).days

    return ProjectRead(
        id=project.id,
        name=project.name,
        description=project.description,
        required_skills=list(project.required_skills or []),
        status=project.status,
        priority=project.priority,
        start_date=project.start_date,
        target_date=project.target_date,
        repo_url=project.repo_url,
        demo_url=project.demo_url,
        notes=project.notes,
        order_index=project.order_index,
        created_at=project.created_at,
        updated_at=project.updated_at,
        milestones=[ProjectMilestoneRead.model_validate(m) for m in milestones],
        checklist_items=[ProjectChecklistItemRead.model_validate(c) for c in checklist_items],
        milestone_count=len(milestones),
        completed_milestones=completed_milestones,
        completion_percentage=round(completed_milestones / len(milestones) * 100, 2)
        if milestones
        else 0.0,
        checklist_count=len(checklist_items),
        completed_checklist_items=completed_checklist,
        checklist_percentage=round(completed_checklist / len(checklist_items) * 100, 2)
        if checklist_items
        else 0.0,
        days_remaining=days_remaining,
    )


def list_projects(db: Session, user_id: uuid.UUID) -> list[ProjectRead]:
    return [_read(p) for p in project_repo.list_projects(db, user_id)]


def get_project(db: Session, user_id: uuid.UUID, project_id: uuid.UUID) -> ProjectRead:
    project = project_repo.get_project(db, user_id, project_id)
    if project is None:
        raise NotFoundError("Project not found", code="project_not_found")
    return _read(project)


def create_project(db: Session, user_id: uuid.UUID, payload: ProjectCreate) -> ProjectRead:
    if project_repo.get_project_by_name(db, user_id, payload.name) is not None:
        raise ConflictError("You already have a project with this name", code="project_name_taken")
    existing = project_repo.list_projects(db, user_id)
    order_index = len(existing) + 1
    project = project_repo.create_project(
        db,
        user_id=user_id,
        name=payload.name,
        description=payload.description,
        required_skills=list(payload.required_skills),
        status=payload.status,
        priority=payload.priority,
        start_date=payload.start_date,
        target_date=payload.target_date,
        repo_url=payload.repo_url,
        demo_url=payload.demo_url,
        notes=payload.notes,
        order_index=order_index,
    )
    db.commit()
    db.refresh(project)
    return get_project(db, user_id, project.id)


def update_project(
    db: Session, user_id: uuid.UUID, project_id: uuid.UUID, payload: ProjectUpdate
) -> ProjectRead:
    project = project_repo.get_project(db, user_id, project_id)
    if project is None:
        raise NotFoundError("Project not found", code="project_not_found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return get_project(db, user_id, project_id)


def delete_project(db: Session, user_id: uuid.UUID, project_id: uuid.UUID) -> None:
    project = project_repo.get_project(db, user_id, project_id)
    if project is None:
        raise NotFoundError("Project not found", code="project_not_found")
    project_repo.delete_project(db, project)
    db.commit()


def create_milestone(
    db: Session, user_id: uuid.UUID, project_id: uuid.UUID, payload: ProjectMilestoneCreate
) -> ProjectMilestoneRead:
    project = project_repo.get_project(db, user_id, project_id)
    if project is None:
        raise NotFoundError("Project not found", code="project_not_found")
    order_index = payload.order_index
    if order_index is None:
        order_index = len(project_repo.list_milestones(db, project_id)) + 1
    milestone = project_repo.create_milestone(
        db,
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        order_index=order_index,
    )
    db.commit()
    db.refresh(milestone)
    return ProjectMilestoneRead.model_validate(milestone)


def update_milestone(
    db: Session,
    user_id: uuid.UUID,
    milestone_id: uuid.UUID,
    payload: ProjectMilestoneUpdate,
) -> ProjectMilestoneRead:
    from datetime import datetime

    milestone = project_repo.get_milestone(db, user_id, milestone_id)
    if milestone is None:
        raise NotFoundError("Milestone not found", code="milestone_not_found")
    data = payload.model_dump(exclude_unset=True)
    if "is_completed" in data and data["is_completed"] is not None:
        milestone.is_completed = data["is_completed"]
        milestone.completed_at = (
            datetime.now(UTC) if data["is_completed"] else None
        )
        data.pop("is_completed")
    for field, value in data.items():
        setattr(milestone, field, value)
    db.commit()
    db.refresh(milestone)
    return ProjectMilestoneRead.model_validate(milestone)


def delete_milestone(db: Session, user_id: uuid.UUID, milestone_id: uuid.UUID) -> None:
    milestone = project_repo.get_milestone(db, user_id, milestone_id)
    if milestone is None:
        raise NotFoundError("Milestone not found", code="milestone_not_found")
    project_repo.delete_milestone(db, milestone)
    db.commit()


def create_checklist_item(
    db: Session, user_id: uuid.UUID, project_id: uuid.UUID, payload: ProjectChecklistItemCreate
) -> ProjectChecklistItemRead:
    project = project_repo.get_project(db, user_id, project_id)
    if project is None:
        raise NotFoundError("Project not found", code="project_not_found")
    item = project_repo.create_checklist_item(
        db, project_id=project_id, title=payload.title, is_done=payload.is_done
    )
    db.commit()
    db.refresh(item)
    return ProjectChecklistItemRead.model_validate(item)


def update_checklist_item(
    db: Session, user_id: uuid.UUID, item_id: uuid.UUID, payload: ProjectChecklistItemUpdate
) -> ProjectChecklistItemRead:
    item = project_repo.get_checklist_item(db, user_id, item_id)
    if item is None:
        raise NotFoundError("Checklist item not found", code="checklist_item_not_found")
    if payload.title is not None:
        item.title = payload.title
    if payload.is_done is not None:
        item.is_done = payload.is_done
    db.commit()
    db.refresh(item)
    return ProjectChecklistItemRead.model_validate(item)


def delete_checklist_item(db: Session, user_id: uuid.UUID, item_id: uuid.UUID) -> None:
    item = project_repo.get_checklist_item(db, user_id, item_id)
    if item is None:
        raise NotFoundError("Checklist item not found", code="checklist_item_not_found")
    project_repo.delete_checklist_item(db, item)
    db.commit()


def summary(db: Session, user_id: uuid.UUID) -> ProjectSummary:
    projects = project_repo.list_projects(db, user_id)
    counts = {ProjectStatus.NOT_STARTED: 0, ProjectStatus.IN_PROGRESS: 0, ProjectStatus.COMPLETED: 0}
    total_percentage = 0.0
    for project in projects:
        counts[project.status] = counts.get(project.status, 0) + 1
        milestones = list(project.milestones or [])
        if milestones:
            total_percentage += sum(1 for m in milestones if m.is_completed) / len(milestones) * 100
    return ProjectSummary(
        total=len(projects),
        not_started=counts.get(ProjectStatus.NOT_STARTED, 0),
        in_progress=counts.get(ProjectStatus.IN_PROGRESS, 0),
        completed=counts.get(ProjectStatus.COMPLETED, 0),
        average_completion=round(total_percentage / len(projects), 2) if projects else 0.0,
    )
