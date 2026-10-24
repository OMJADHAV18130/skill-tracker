"""Project tracker data access."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.project import (
    Project,
    ProjectChecklistItem,
    ProjectMilestone,
    ProjectStatus,
)


def list_projects(db: Session, user_id: uuid.UUID) -> list[Project]:
    stmt = (
        select(Project)
        .options(selectinload(Project.milestones), selectinload(Project.checklist_items))
        .where(Project.user_id == user_id)
        .order_by(Project.order_index, Project.created_at)
    )
    return list(db.scalars(stmt).unique().all())


def get_project(db: Session, user_id: uuid.UUID, project_id: uuid.UUID) -> Project | None:
    stmt = (
        select(Project)
        .options(selectinload(Project.milestones), selectinload(Project.checklist_items))
        .where(Project.user_id == user_id, Project.id == project_id)
    )
    return db.scalar(stmt)


def get_project_by_name(db: Session, user_id: uuid.UUID, name: str) -> Project | None:
    return db.scalar(select(Project).where(Project.user_id == user_id, Project.name == name))


def create_project(db: Session, *, user_id: uuid.UUID, **values) -> Project:
    project = Project(user_id=user_id, **values)
    db.add(project)
    db.flush()
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.flush()


def list_milestones(db: Session, project_id: uuid.UUID) -> list[ProjectMilestone]:
    return list(
        db.scalars(
            select(ProjectMilestone)
            .where(ProjectMilestone.project_id == project_id)
            .order_by(ProjectMilestone.order_index, ProjectMilestone.created_at)
        ).all()
    )


def get_milestone(
    db: Session, user_id: uuid.UUID, milestone_id: uuid.UUID
) -> ProjectMilestone | None:
    """Scope by user through the parent project so ownership is guaranteed."""
    return db.scalar(
        select(ProjectMilestone)
        .join(Project, ProjectMilestone.project_id == Project.id)
        .where(Project.user_id == user_id, ProjectMilestone.id == milestone_id)
    )


def create_milestone(db: Session, *, project_id: uuid.UUID, **values) -> ProjectMilestone:
    milestone = ProjectMilestone(project_id=project_id, **values)
    db.add(milestone)
    db.flush()
    return milestone


def delete_milestone(db: Session, milestone: ProjectMilestone) -> None:
    db.delete(milestone)
    db.flush()


def list_checklist_items(db: Session, project_id: uuid.UUID) -> list[ProjectChecklistItem]:
    return list(
        db.scalars(
            select(ProjectChecklistItem)
            .where(ProjectChecklistItem.project_id == project_id)
            .order_by(ProjectChecklistItem.order_index, ProjectChecklistItem.created_at)
        ).all()
    )


def get_checklist_item(
    db: Session, user_id: uuid.UUID, item_id: uuid.UUID
) -> ProjectChecklistItem | None:
    return db.scalar(
        select(ProjectChecklistItem)
        .join(Project, ProjectChecklistItem.project_id == Project.id)
        .where(Project.user_id == user_id, ProjectChecklistItem.id == item_id)
    )


def create_checklist_item(
    db: Session, *, project_id: uuid.UUID, title: str, is_done: bool = False
) -> ProjectChecklistItem:
    order_index = len(list_checklist_items(db, project_id))
    item = ProjectChecklistItem(
        project_id=project_id, title=title, is_done=is_done, order_index=order_index
    )
    db.add(item)
    db.flush()
    return item


def delete_checklist_item(db: Session, item: ProjectChecklistItem) -> None:
    db.delete(item)
    db.flush()


def status_counts(db: Session, user_id: uuid.UUID) -> dict[ProjectStatus, int]:
    stmt = (
        select(Project.status, func.count())
        .where(Project.user_id == user_id)
        .group_by(Project.status)
    )
    return {row[0]: int(row[1]) for row in db.execute(stmt).all()}
