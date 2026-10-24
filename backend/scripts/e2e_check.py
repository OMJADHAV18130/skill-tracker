r"""End-to-end API check against a real PostgreSQL database.

This is intentionally *not* part of pytest: it starts an isolated PostgreSQL
cluster, runs the real Alembic migration and seed CLI, then exercises the API
through Starlette's TestClient with separate clients/users.

Usage (from ``backend/``):

    .\.venv\Scripts\python.exe -m scripts.e2e_check

It verifies:
- migrations + shared seed (9 phases / 93 topics, 7 core and 2 DSA)
- registration scaffolding (6 projects per learner)
- progress persistence and idempotent completion/re-opening
- study logging and dashboard derivation
- cross-user isolation for tasks, progress, resources, bookmarks and settings
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import uuid
from datetime import date, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
PGDATA = ROOT / ".e2e-pgdata"
DB_NAME = "devpath_e2e"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
    print(f"ok   {message}")


def main() -> None:
    try:
        import pgserver
    except ImportError:
        fail("pgserver is not installed. Run `uv pip install -r requirements.txt` first.")

    PGDATA.mkdir(parents=True, exist_ok=True)
    server = pgserver.get_server(PGDATA, cleanup_mode=None)
    server.psql(f"DROP DATABASE IF EXISTS {DB_NAME} WITH (FORCE)")
    server.psql(f"CREATE DATABASE {DB_NAME}")
    uri = server.get_uri()
    host_port = uri.split("@", 1)[1].split("/", 1)[0]
    database_url = f"postgresql+psycopg://postgres@{host_port}/{DB_NAME}"
    print(f"PostgreSQL ready at {host_port}, database={DB_NAME}")

    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": database_url,
            "ENVIRONMENT": "test",
            "DEBUG": "false",
            "SECRET_KEY": "e2e-only-secret-key-not-for-production",
            "SEED_ON_STARTUP": "false",
            "BCRYPT_ROUNDS": "4",
            "LOG_LEVEL": "WARNING",
            "LOG_FORMAT": "text",
        }
    )

    print("Running Alembic migration...")
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        check=True,
    )

    print("Seeding shared roadmap and demo account...")
    subprocess.run(
        [sys.executable, "-m", "app.db.seed"],
        cwd=ROOT,
        env=env,
        check=True,
    )

    # The API settings are loaded after the environment is set, so the app
    # connects to the isolated cluster above.
    os.environ.update(env)

    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app()

    stamp = uuid.uuid4().hex[:8]
    alice_payload = {
        "email": f"alice-{stamp}@example.com",
        "username": f"alice{stamp}",
        "full_name": "Alice E2E",
        "password": "S3cure-pass!",
    }
    bob_payload = {
        "email": f"bob-{stamp}@example.com",
        "username": f"bob{stamp}",
        "full_name": "Bob E2E",
        "password": "S3cure-pass!",
    }

    with TestClient(app) as client:
        alice = client.post("/api/v1/auth/register", json=alice_payload)
        bob = client.post("/api/v1/auth/register", json=bob_payload)
        expect(alice.status_code == 201, "Alice can register")
        expect(bob.status_code == 201, "Bob can register")
        alice_headers = {"Authorization": f"Bearer {alice.json()['access_token']}"}
        bob_headers = {"Authorization": f"Bearer {bob.json()['access_token']}"}

        alice_projects = client.get("/api/v1/projects", headers=alice_headers)
        expect(alice_projects.status_code == 200, "Alice can load projects")
        expect(
            len(alice_projects.json()) == 6,
            "registration scaffolds exactly six projects",
        )

        phases = client.get("/api/v1/roadmap/phases", headers=alice_headers).json()
        expect(len(phases["items"]) == 7, "seven core roadmap phases are seeded")
        expect(phases["total_topics"] == 69, "69 core topics are seeded")
        expect(phases["completed_topics"] == 0, "new learners start at zero progress")

        dsa_phases = client.get(
            "/api/v1/roadmap/phases?track=dsa", headers=alice_headers
        ).json()
        expect(len(dsa_phases["items"]) == 2, "two parallel DSA phases are seeded")
        expect(dsa_phases["total_topics"] == 24, "24 DSA topics are seeded")

        topic = phases["items"][0]["topics"][0]
        progress_url = f"/api/v1/roadmap/topics/{topic['id']}/progress"
        first = client.patch(
            progress_url, json={"status": "completed", "rating": 5}, headers=alice_headers
        )
        expect(first.status_code == 200, "topic can be marked completed")
        completed_at = first.json()["progress"]["completed_at"]
        expect(completed_at is not None, "completion timestamp is persisted")

        again = client.patch(
            progress_url, json={"status": "completed"}, headers=alice_headers
        ).json()
        expect(
            again["progress"]["completed_at"] == completed_at,
            "re-completing a topic is idempotent",
        )
        refreshed = client.get("/api/v1/roadmap/phases", headers=alice_headers).json()
        expect(refreshed["completed_topics"] == 1, "completed count is not double-counted")

        client.patch(progress_url, json={"status": "not_started"}, headers=alice_headers)
        reopened = client.get("/api/v1/roadmap/phases", headers=alice_headers).json()
        expect(reopened["completed_topics"] == 0, "re-opening a topic removes it from progress")
        client.patch(progress_url, json={"status": "completed"}, headers=alice_headers)
        recompleted = client.get("/api/v1/roadmap/phases", headers=alice_headers).json()
        expect(recompleted["completed_topics"] == 1, "re-completion restores exactly one topic")

        bob_phases = client.get("/api/v1/roadmap/phases", headers=bob_headers).json()
        expect(
            bob_phases["completed_topics"] == 0,
            "topic progress is isolated per user",
        )

        today = date.today().isoformat()
        task = client.post(
            "/api/v1/planner/tasks",
            json={
                "title": "E2E study task",
                "task_date": today,
                "estimated_minutes": 45,
                "category": "Spring Boot",
                "priority": "high",
            },
            headers=alice_headers,
        )
        expect(task.status_code == 201, "Alice can create a planner task")
        task_id = task.json()["id"]

        logged = client.post(
            f"/api/v1/planner/tasks/{task_id}/log",
            json={"actual_minutes": 30, "session_note": "E2E session", "completed": True},
            headers=alice_headers,
        )
        expect(logged.status_code == 200, "study time can be logged against a task")
        expect(logged.json()["actual_minutes"] == 30, "logged minutes are stored")

        alice_tasks = client.get("/api/v1/planner/tasks", headers=alice_headers).json()
        bob_tasks = client.get("/api/v1/planner/tasks", headers=bob_headers).json()
        expect(alice_tasks["meta"]["total"] == 1, "Alice sees her own task")
        expect(bob_tasks["meta"]["total"] == 0, "Bob cannot see Alice's task")
        expect(
            client.patch(
                f"/api/v1/planner/tasks/{task_id}",
                json={"title": "Hijacked"},
                headers=bob_headers,
            ).status_code
            == 404,
            "Bob cannot update Alice's task",
        )

        alice_dashboard = client.get("/api/v1/dashboard", headers=alice_headers).json()
        bob_dashboard = client.get("/api/v1/dashboard", headers=bob_headers).json()
        expect(alice_dashboard["total_study_minutes"] == 30, "dashboard derives study minutes")
        expect(alice_dashboard["completed_topics"] == 1, "dashboard derives topic progress")
        expect(alice_dashboard["current_streak"] >= 1, "dashboard derives the study streak")
        expect(bob_dashboard["total_study_minutes"] == 0, "Bob's dashboard is unaffected")
        expect(bob_dashboard["completed_topics"] == 0, "Bob's progress is unaffected")

        demo_login = client.post(
            "/api/v1/auth/login",
            json={"email": "demo@devpath.dev", "password": "devpath-demo-123"},
        )
        expect(demo_login.status_code == 200, "documented demo account can sign in")
        demo_headers = {"Authorization": f"Bearer {demo_login.json()['access_token']}"}
        demo_dashboard = client.get("/api/v1/dashboard", headers=demo_headers).json()
        expect(demo_dashboard["completed_topics"] > 0, "demo account has seeded progress")
        expect(demo_dashboard["total_study_minutes"] > 0, "demo account has seeded study time")

        official = client.get("/api/v1/resources", headers=alice_headers).json()
        expect(official["total"] >= 11, "verified official documentation is seeded")
        resource_id = official["items"][0]["id"]
        client.put(
            f"/api/v1/resources/{resource_id}/bookmark",
            json={"is_bookmarked": True},
            headers=alice_headers,
        )
        bob_resources = client.get("/api/v1/resources", headers=bob_headers).json()
        expect(
            bob_resources["bookmarked_count"] == 0,
            "bookmarks are isolated per user",
        )

        custom = client.post(
            "/api/v1/resources",
            json={
                "title": "Alice's private notes",
                "url": "https://example.com/alice",
                "description": "Private bookmark",
                "category": "Java",
                "tags": ["private"],
            },
            headers=alice_headers,
        )
        expect(custom.status_code == 201, "custom resources can be created")
        custom_id = custom.json()["id"]
        expect(
            client.get(f"/api/v1/resources/{custom_id}", headers=bob_headers).status_code == 404,
            "custom resources are private to their owner",
        )

        settings_update = client.patch(
            "/api/v1/settings", json={"daily_goal_minutes": 90}, headers=alice_headers
        )
        expect(settings_update.status_code == 200, "preferences can be updated")
        expect(
            settings_update.json()["daily_goal_minutes"] == 90,
            "updated daily goal is persisted",
        )
        bob_settings = client.get("/api/v1/settings", headers=bob_headers).json()
        expect(
            bob_settings["daily_goal_minutes"] != 90,
            "preferences are isolated per user",
        )

        paused = client.post(
            "/api/v1/settings/dsa/pause",
            json={"resume_on": (date.today() + timedelta(days=7)).isoformat()},
            headers=alice_headers,
        )
        expect(paused.status_code == 200, "the DSA track can be paused")
        expect(paused.json()["dsa_paused"] is True, "the DSA pause is persisted")
        alice_dashboard_paused = client.get(
            "/api/v1/dashboard", headers=alice_headers
        ).json()
        expect(
            alice_dashboard_paused["dsa"]["paused"] is True,
            "the dashboard reflects the paused DSA track",
        )
        resumed = client.post("/api/v1/settings/dsa/resume", headers=alice_headers)
        expect(resumed.status_code == 200, "the DSA track can be resumed")
        expect(resumed.json()["dsa_paused"] is False, "the DSA pause is cleared")

        export = client.get("/api/v1/settings/export.json", headers=alice_headers)
        expect(export.status_code == 200, "JSON export works")
        expect("topic_progress" in export.json(), "export contains topic progress")

    # A brand-new client and a fresh login must still see the persisted data.
    with TestClient(app) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"email": alice_payload["email"], "password": alice_payload["password"]},
        )
        expect(login.status_code == 200, "Alice can sign in again")
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        persisted = client.get("/api/v1/roadmap/phases", headers=headers).json()
        expect(persisted["completed_topics"] == 1, "progress survives a new login and client")
        tasks = client.get("/api/v1/planner/tasks", headers=headers).json()
        expect(tasks["meta"]["total"] == 1, "planner data survives a new client")

    print("\nChecking migration downgrade/upgrade round-trip...")
    from sqlalchemy import text

    from app.db.session import engine

    engine.dispose()
    subprocess.run(
        [sys.executable, "-m", "alembic", "downgrade", "base"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "app.db.seed", "--no-demo"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    with engine.connect() as conn:
        phase_count = conn.execute(text("SELECT count(*) FROM roadmap_phases")).scalar_one()
        topic_count = conn.execute(text("SELECT count(*) FROM topics")).scalar_one()
    expect(
        phase_count == 9 and topic_count == 93,
        "migrations roll back and re-apply cleanly",
    )

    print("\nE2E check passed: persistence, isolation and migrations verified.")


if __name__ == "__main__":
    main()
