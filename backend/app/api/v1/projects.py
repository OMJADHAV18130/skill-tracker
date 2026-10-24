"""Project tracker endpoints."""

from __future__ import annotations

import uuid
from datetime import UTC

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
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
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead], summary="List the user's projects")
def list_projects(db: DbSession, current_user: CurrentUser) -> list[ProjectRead]:
    return project_service.list_projects(db, current_user.id)


@router.get("/summary", response_model=ProjectSummary, summary="Aggregate project stats")
def summary(db: DbSession, current_user: CurrentUser) -> ProjectSummary:
    return project_service.summary(db, current_user.id)


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
def create_project(
    payload: ProjectCreate, db: DbSession, current_user: CurrentUser
) -> ProjectRead:
    return project_service.create_project(db, current_user.id, payload)


@router.get("/{project_id}", response_model=ProjectRead, summary="Get a project")
def get_project(project_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> ProjectRead:
    return project_service.get_project(db, current_user.id, project_id)


@router.patch("/{project_id}", response_model=ProjectRead, summary="Update a project")
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectRead:
    return project_service.update_project(db, current_user.id, project_id, payload)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
)
def delete_project(project_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> None:
    project_service.delete_project(db, current_user.id, project_id)


@router.post(
    "/{project_id}/milestones",
    response_model=ProjectMilestoneRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a milestone to a project",
)
def create_milestone(
    project_id: uuid.UUID,
    payload: ProjectMilestoneCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectMilestoneRead:
    return project_service.create_milestone(db, current_user.id, project_id, payload)


@router.patch(
    "/milestones/{milestone_id}",
    response_model=ProjectMilestoneRead,
    summary="Update a milestone",
)
def update_milestone(
    milestone_id: uuid.UUID,
    payload: ProjectMilestoneUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectMilestoneRead:
    return project_service.update_milestone(db, current_user.id, milestone_id, payload)


@router.delete(
    "/milestones/{milestone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a milestone",
)
def delete_milestone(
    milestone_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> None:
    project_service.delete_milestone(db, current_user.id, milestone_id)


@router.post(
    "/{project_id}/checklist",
    response_model=ProjectChecklistItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a checklist item to a project",
)
def create_checklist_item(
    project_id: uuid.UUID,
    payload: ProjectChecklistItemCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectChecklistItemRead:
    return project_service.create_checklist_item(db, current_user.id, project_id, payload)


@router.patch(
    "/checklist/{item_id}",
    response_model=ProjectChecklistItemRead,
    summary="Update a project checklist item",
)
def update_checklist_item(
    item_id: uuid.UUID,
    payload: ProjectChecklistItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectChecklistItemRead:
    return project_service.update_checklist_item(db, current_user.id, item_id, payload)


@router.delete(
    "/checklist/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project checklist item",
)
def delete_checklist_item(
    item_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> None:
    project_service.delete_checklist_item(db, current_user.id, item_id)


@router.post(
    "/{project_id}/complete",
    response_model=ProjectRead,
    summary="Mark every milestone of a project complete",
)
def complete_project(
    project_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> ProjectRead:
    from datetime import datetime

    from app.core.errors import NotFoundError
    from app.repositories import project_repo

    project = project_repo.get_project(db, current_user.id, project_id)
    if project is None:
        raise NotFoundError("Project not found", code="project_not_found")
    for milestone in project.milestones or []:
        if not milestone.is_completed:
            milestone.is_completed = True
            milestone.completed_at = datetime.now(UTC)
    project.status = project_service.ProjectStatus.COMPLETED
    db.commit()
    return project_service.get_project(db, current_user.id, project_id)
