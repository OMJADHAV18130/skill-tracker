"""Authorization / data ownership tests.

Every private record must be scoped to the authenticated user. A user id in a
request body is never trusted.
"""

from __future__ import annotations

from datetime import date


def _first_topic_id(client, headers) -> str:
    phases = client.get("/api/v1/roadmap/phases", headers=headers).json()
    return phases["items"][0]["topics"][0]["id"]


def _first_project(client, headers) -> dict:
    return client.get("/api/v1/projects", headers=headers).json()[0]


class TestTaskOwnership:
    def test_cannot_read_another_users_task(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()

        created = client.post(
            "/api/v1/planner/tasks",
            json={"title": "Alice private task", "task_date": date.today().isoformat()},
            headers=alice["headers"],
        )
        assert created.status_code == 201
        task_id = created.json()["id"]

        assert client.get(f"/api/v1/planner/tasks/{task_id}", headers=bob["headers"]).status_code == 404
        assert (
            client.patch(
                f"/api/v1/planner/tasks/{task_id}",
                json={"title": "Hijacked"},
                headers=bob["headers"],
            ).status_code
            == 404
        )
        assert (
            client.delete(f"/api/v1/planner/tasks/{task_id}", headers=bob["headers"]).status_code
            == 404
        )

    def test_task_lists_are_isolated(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()
        client.post(
            "/api/v1/planner/tasks",
            json={"title": "Only Alice", "task_date": date.today().isoformat()},
            headers=alice["headers"],
        )
        bob_tasks = client.get("/api/v1/planner/tasks", headers=bob["headers"]).json()
        assert bob_tasks["items"] == []
        assert bob_tasks["meta"]["total"] == 0

    def test_user_id_in_body_is_ignored(self, client, user_factory):
        """A client cannot create a record on behalf of another user."""
        alice = user_factory()
        bob = user_factory()

        response = client.post(
            "/api/v1/planner/tasks",
            json={
                "title": "Spoofed",
                "task_date": date.today().isoformat(),
                "user_id": alice["user"]["id"],
            },
            headers=bob["headers"],
        )
        assert response.status_code == 201

        alice_tasks = client.get("/api/v1/planner/tasks", headers=alice["headers"]).json()
        assert all(task["title"] != "Spoofed" for task in alice_tasks["items"])


class TestStudySessionOwnership:
    def test_cannot_delete_another_users_session(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()
        session = client.post(
            "/api/v1/planner/sessions",
            json={"minutes": 45, "session_date": date.today().isoformat()},
            headers=alice["headers"],
        ).json()
        assert (
            client.delete(
                f"/api/v1/planner/sessions/{session['id']}", headers=bob["headers"]
            ).status_code
            == 404
        )
        # Alice still has it.
        remaining = client.get("/api/v1/planner/sessions", headers=alice["headers"]).json()
        assert len(remaining) == 1


class TestTopicOwnership:
    def test_topic_progress_is_per_user(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()
        topic_id = _first_topic_id(client, alice["headers"])

        response = client.patch(
            f"/api/v1/roadmap/topics/{topic_id}/progress",
            json={"status": "completed"},
            headers=alice["headers"],
        )
        assert response.status_code == 200
        assert response.json()["progress"]["status"] == "completed"

        bob_topic = client.get(
            f"/api/v1/roadmap/topics/{topic_id}", headers=bob["headers"]
        ).json()
        assert bob_topic["progress"]["status"] == "not_started"

    def test_notes_are_private(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()
        topic_id = _first_topic_id(client, alice["headers"])

        note = client.post(
            f"/api/v1/roadmap/topics/{topic_id}/notes",
            json={"content": "Alice's secret note"},
            headers=alice["headers"],
        ).json()

        bob_notes = client.get(
            f"/api/v1/roadmap/topics/{topic_id}/notes", headers=bob["headers"]
        ).json()
        assert bob_notes == []

        assert (
            client.patch(
                f"/api/v1/roadmap/notes/{note['id']}",
                json={"content": "Hijacked"},
                headers=bob["headers"],
            ).status_code
            == 404
        )
        assert (
            client.delete(f"/api/v1/roadmap/notes/{note['id']}", headers=bob["headers"]).status_code
            == 404
        )

    def test_checklist_is_private(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()
        topic_id = _first_topic_id(client, alice["headers"])

        item = client.post(
            f"/api/v1/roadmap/topics/{topic_id}/checklist",
            json={"title": "Alice checklist"},
            headers=alice["headers"],
        ).json()

        assert client.get(
            f"/api/v1/roadmap/topics/{topic_id}/checklist", headers=bob["headers"]
        ).json() == []
        assert (
            client.patch(
                f"/api/v1/roadmap/checklist/{item['id']}",
                json={"is_done": True},
                headers=bob["headers"],
            ).status_code
            == 404
        )


class TestProjectOwnership:
    def test_cannot_read_another_users_project(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()
        project = _first_project(client, alice["headers"])

        assert (
            client.get(f"/api/v1/projects/{project['id']}", headers=bob["headers"]).status_code
            == 404
        )

    def test_cannot_modify_another_users_milestone(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()
        project = _first_project(client, alice["headers"])
        milestone = project["milestones"][0]

        response = client.patch(
            f"/api/v1/projects/milestones/{milestone['id']}",
            json={"is_completed": True},
            headers=bob["headers"],
        )
        assert response.status_code == 404

        refreshed = client.get(
            f"/api/v1/projects/{project['id']}", headers=alice["headers"]
        ).json()
        assert refreshed["completed_milestones"] == 0

    def test_each_user_gets_their_own_seeded_projects(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()
        alice_projects = client.get("/api/v1/projects", headers=alice["headers"]).json()
        bob_projects = client.get("/api/v1/projects", headers=bob["headers"]).json()
        assert len(alice_projects) == 6
        assert len(bob_projects) == 6
        assert {p["id"] for p in alice_projects}.isdisjoint({p["id"] for p in bob_projects})


class TestResourceOwnership:
    def test_bookmarks_are_per_user(self, client, user_factory):
        alice = user_factory()
        bob = user_factory()
        resources = client.get("/api/v1/resources", headers=alice["headers"]).json()
        resource_id = resources["items"][0]["id"]

        client.put(
            f"/api/v1/resources/{resource_id}/bookmark",
            json={"is_bookmarked": True},
            headers=alice["headers"],
        )

        bob_resource = client.get(
            f"/api/v1/resources/{resource_id}", headers=bob["headers"]
        ).json()
        assert bob_resource["is_bookmarked"] is False
