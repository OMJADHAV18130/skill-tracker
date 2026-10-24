"""Logging configuration. Passwords, tokens and secrets are never logged."""

from __future__ import annotations

import json
import logging
import logging.config
import sys
from typing import Any

from app.core.config import settings

SENSITIVE_KEYS = {
    "password",
    "new_password",
    "current_password",
    "confirm_password",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "secret",
    "secret_key",
    "hashed_password",
    "api_key",
}

REDACTED = "[REDACTED]"


class RedactingFilter(logging.Filter):
    """Scrub sensitive keys from structured log records."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        for key in list(record.__dict__.keys()):
            if key.lower() in SENSITIVE_KEYS:
                record.__dict__[key] = REDACTED
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
        }
        for key in ("path", "method", "status_code", "user_id", "request_id"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        extras = {
            key: getattr(record, key)
            for key in ("path", "method", "status_code", "user_id")
            if getattr(record, key, None) is not None
        }
        if extras:
            base = f"{base} | {' '.join(f'{k}={v}' for k, v in extras.items())}"
        return base


def configure_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RedactingFilter())
    if settings.log_format.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            TextFormatter("%(asctime)s %(levelname)-8s %(name)s | %(message)s")
        )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    for noisy in ("uvicorn.access", "sqlalchemy.engine.Engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING if noisy.startswith("uvicorn") else level)
