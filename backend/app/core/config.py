"""Application configuration loaded from environment variables / .env file."""

from __future__ import annotations

import functools
from typing import Annotated, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # `.env.local` is written by `python -m scripts.local_postgres` and takes
        # precedence so a local database can be selected without editing `.env`.
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- App ---------------------------------------------------------------
    app_name: str = "DevPath API"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    docs_url: str | None = "/docs"
    openapi_url: str | None = "/openapi.json"

    # --- Database ----------------------------------------------------------
    database_url: str = "postgresql+psycopg://devpath:devpath@localhost:5432/devpath"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False
    db_connect_timeout: int = 10

    # --- Security ----------------------------------------------------------
    secret_key: str = "change-me-to-a-long-random-string-before-production-use"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    bcrypt_rounds: int = 12

    # --- CORS --------------------------------------------------------------
    # ``NoDecode`` keeps pydantic-settings from trying to JSON-parse the value
    # first so the validator below can accept a plain comma separated string.
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # --- Seeding -----------------------------------------------------------
    seed_on_startup: bool = True
    demo_user_email: str = "demo@devpath.dev"
    demo_user_username: str = "demo"
    demo_user_password: str = "devpath-demo-123"
    demo_user_full_name: str = "Demo Learner"

    # --- Logging -----------------------------------------------------------
    log_level: str = "INFO"
    log_format: str = "json"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: Any) -> Any:
        """Accept both a JSON array and a comma separated string."""
        if isinstance(value, str):
            raw = value.strip()
            if raw.startswith("["):
                return value  # let pydantic parse the JSON form
            return [item.strip() for item in raw.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    @property
    def sync_database_url(self) -> str:
        """Normalise the URL so SQLAlchemy always uses the sync psycopg driver."""
        url = self.database_url
        for prefix in ("postgresql+asyncpg", "postgres+asyncpg"):
            url = url.replace(prefix, "postgresql+psycopg")
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
