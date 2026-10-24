"""API v1 router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth, dashboard, health, planner, projects, resources, roadmap, settings

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(roadmap.router)
api_router.include_router(planner.router)
api_router.include_router(projects.router)
api_router.include_router(resources.router)
api_router.include_router(settings.router)
