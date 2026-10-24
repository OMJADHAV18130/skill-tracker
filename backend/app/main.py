"""DevPath API application factory."""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging_config import configure_logging

logger = logging.getLogger("devpath")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info(
        "Starting %s (environment=%s)", settings.app_name, settings.environment
    )

    if settings.seed_on_startup:
        try:
            from app.db.seed import run_full_seed
            from app.db.session import SessionLocal

            with SessionLocal() as db:
                result = run_full_seed(db)
            logger.info("Seed complete: %s", result)
        except Exception as exc:  # pragma: no cover - startup resilience
            logger.error("Seeding failed (continuing without it): %s", exc)

    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description=(
            "DevPath - a personal learning roadmap and progress tracker for becoming a "
            "Backend + DevOps Engineer with Java and Spring Boot.\n\n"
            "All routes are versioned under `/api/v1`. Private resources require a "
            "`Authorization: Bearer <access token>` header.\n\n"
            "**Demo account** (local development): "
            f"`{settings.demo_user_email}` / `{settings.demo_user_password}`"
        ),
        docs_url=settings.docs_url,
        redoc_url="/redoc",
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
        contact={"name": "DevPath", "url": "https://github.com/your-org/devpath"},
        license_info={"name": "MIT"},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "unhandled_exception path=%s method=%s request_id=%s",
                request.url.path,
                request.method,
                request_id,
            )
            raise
        duration_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = f"{duration_ms:.1f}"
        logger.info(
            "request path=%s method=%s status=%s duration_ms=%.1f",
            request.url.path,
            request.method,
            response.status_code,
            duration_ms,
        )
        return response

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", include_in_schema=False)
    def root() -> JSONResponse:
        return JSONResponse(
            {
                "name": settings.app_name,
                "version": "1.0.0",
                "docs": "/docs",
                "api": settings.api_v1_prefix,
                "health": f"{settings.api_v1_prefix}/health",
            }
        )

    return app


app = create_app()
