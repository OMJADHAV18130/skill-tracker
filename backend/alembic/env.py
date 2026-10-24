"""Alembic environment - the URL comes from the application settings."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from app.core.config import settings
from app.db.base import Base

# Import the models so that ``Base.metadata`` is complete.
from app import models  # noqa: F401,E402

config = context.config
# ``sqlalchemy.url`` is still set for offline mode, but configparser treats
# ``%`` as interpolation, so escape it here.
config.set_main_option("sqlalchemy.url", settings.sync_database_url.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live connection (emits SQL to stdout)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database."""
    # Build the engine from the raw URL instead of going through
    # ``engine_from_config`` so percent-encoded passwords survive intact.
    from sqlalchemy import create_engine

    connectable = create_engine(settings.sync_database_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
