"""Pytest fixtures.

The test suite runs against a real PostgreSQL instance. It will use, in order:

1. ``TEST_DATABASE_URL`` if set (e.g. a Docker PostgreSQL),
2. an in-process PostgreSQL started with the ``pgserver`` dev dependency,
3. SQLite as a last resort (portable but less representative).

Each test runs inside an outer transaction that is rolled back afterwards, so
tests never see each other's data while the shared roadmap seed is computed
only once per session.
"""

from __future__ import annotations

import os
import pathlib
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

BACKEND_ROOT = pathlib.Path(__file__).resolve().parents[2]
PGDATA = BACKEND_ROOT / ".pytest-pgdata"


# ---------------------------------------------------------------------------
# Database engine
# ---------------------------------------------------------------------------
def _pgserver_url() -> str | None:
    try:
        import pgserver
    except ImportError:
        return None

    PGDATA.mkdir(parents=True, exist_ok=True)
    server = pgserver.get_server(PGDATA, cleanup_mode=None)
    uri = server.get_uri()  # postgresql://postgres:@127.0.0.1:PORT/postgres

    # Create a dedicated test database.
    exists = server.psql("SELECT 1 FROM pg_database WHERE datname = 'devpath_test'")
    if "1" not in exists.rsplit("\n", 2)[0].split("\n")[-1]:
        try:
            server.psql("CREATE DATABASE devpath_test")
        except Exception:
            pass

    host_port = uri.split("@", 1)[1].split("/", 1)[0]
    return f"postgresql+psycopg://postgres@{host_port}/devpath_test"


@pytest.fixture(scope="session")
def database_url() -> str:
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        return explicit
    url = _pgserver_url()
    if url:
        return url
    sqlite_path = BACKEND_ROOT / ".pytest.sqlite3"
    return f"sqlite+pysqlite:///{sqlite_path.as_posix()}"


@pytest.fixture(scope="session")
def engine(database_url: str):
    is_sqlite = database_url.startswith("sqlite")
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if is_sqlite else {},
    )

    from app import models  # noqa: F401
    from app.db.base import Base

    # Fresh schema for the test run.
    if not is_sqlite:
        with engine.begin() as connection:
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
    Base.metadata.create_all(bind=engine)

    # Seed the shared roadmap exactly once.
    from app.db.seed import seed_shared_roadmap

    with Session(engine) as session:
        seed_shared_roadmap(session)

    yield engine
    engine.dispose()


@pytest.fixture()
def db(engine) -> Session:
    """A session wrapped in an outer transaction that is always rolled back."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def app(engine, db, monkeypatch):
    from app.api import deps
    from app.core.config import settings
    from app.main import create_app

    monkeypatch.setattr(settings, "seed_on_startup", False)
    monkeypatch.setattr(settings, "bcrypt_rounds", 4)  # keep hashing fast in tests

    application = create_app()
    application.dependency_overrides[deps.get_db] = lambda: db
    return application


@pytest.fixture()
def client(app) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
@pytest.fixture()
def user_factory(client):
    counter = {"n": 0}

    def create(email: str | None = None, password: str = "S3cure-pass!"):
        counter["n"] += 1
        payload = {
            "email": email or f"user{counter['n']}-{uuid.uuid4().hex[:6]}@example.com",
            "username": f"user{counter['n']}{uuid.uuid4().hex[:6]}",
            "full_name": f"Test User {counter['n']}",
            "password": password,
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201, response.text
        body = response.json()
        return {
            "payload": payload,
            "tokens": body,
            "headers": {"Authorization": f"Bearer {body['access_token']}"},
            "user": body["user"],
        }

    return create


@pytest.fixture()
def auth_user(user_factory):
    return user_factory()


@pytest.fixture()
def auth_headers(auth_user):
    return auth_user["headers"]
