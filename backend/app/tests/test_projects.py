"""Project tracker tests."""

from __future__ import annotations

from datetime import date, timedelta


def iso(offset: int = 0) -> str:
    return (date.today() + timedelta(days=offset)).isoformat()


class TestSeedProjects:
    def test_new_users_get_the_six_starter_projects(self, client, auth_headers):
        response = client.get("/api/v1/projects", headers=auth_headers)
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 6
        assert {p["name"] for p in projects} >= {"Java Expense Tracker"}
        for project in projects:
            assert project["milestone_count"] > 0
            assert project["checklist_count"] > 0
            assert project["completed_milestones"] == 0
            assert project["completion_percentage"] == 0.0
            assert project["status"] == "not_started"

    def test_summary_reflects_seeded_projects(self, client, auth_headers):
        body = client.get("/api/v1/projects/summary", headers=auth_headers).json()
        assert body["total"] == 6
        assert body["not_started"] == 6
        assert body["in_progress"] == 0
        assert body["completed"] == 0
        assert body["average_completion"] == 0.0


class TestProjectCrud:
    def test_create_read_update_delete(self, client, auth_headers):
        payload = {
            "name": "Realtime Chat",
            "description": "WebSocket chat with Redis pub/sub.",
            "required_skills": ["Java", "Spring Boot", "Redis"],
            "priority": "high",
            "start_date": iso(),
            "target_date": iso(60),
            "repo_url": "https://github.com/me/realtime-chat",
        }
        created = client.post("/api/v1/projects", json=payload, headers=auth_headers)
        assert created.status_code == 201, created.text
        project = created.json()
        assert project["name"] == "Realtime Chat"
        assert project["priority"] == "high"
        assert project["days_remaining"] == 60

        updated = client.patch(
            f"/api/v1/projects/{project['id']}",
            json={"status": "in_progress", "notes": "Kicked off"},
            headers=auth_headers,
        )
        assert updated.status_code == 200
        assert updated.json()["status"] == "in_progress"
        assert updated.json()["notes"] == "Kicked off"

        deleted = client.delete(f"/api/v1/projects/{project['id']}", headers=auth_headers)
        assert deleted.status_code == 204
        assert (
            client.get(f"/api/v1/projects/{project['id']}", headers=auth_headers).status_code
            == 404
        )

    def test_duplicate_project_name_is_rejected(self, client, auth_headers):
        existing = client.get("/api/v1/projects", headers=auth_headers).json()[0]
        response = client.post(
            "/api/v1/projects",
            json={"name": existing["name"]},
            headers=auth_headers,
        )
        assert response.status_code in (409, 422)

    def test_urls_must_be_http(self, client, auth_headers):
        response = client.post(
            "/api/v1/projects",
            json={"name": "Bad URL", "repo_url": "ftp://example.com/repo"},
            headers=auth_headers,
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"


class TestMilestonesAndChecklist:
    def test_milestone_completion_updates_percentage(self, client, auth_headers):
        project = client.get("/api/v1/projects", headers=auth_headers).json()[0]
        total = project["milestone_count"]

        milestone = client.post(
            f"/api/v1/projects/{project['id']}/milestones",
            json={"title": "Add CI pipeline", "due_date": iso(10)},
            headers=auth_headers,
        )
        assert milestone.status_code == 201
        milestone_id = milestone.json()["id"]

        patched = client.patch(
            f"/api/v1/projects/milestones/{milestone_id}",
            json={"is_completed": True},
            headers=auth_headers,
        )
        assert patched.status_code == 200
        assert patched.json()["is_completed"] is True
        assert patched.json()["completed_at"] is not None

        refreshed = client.get(f"/api/v1/projects/{project['id']}", headers=auth_headers).json()
        assert refreshed["completed_milestones"] == 1
        assert refreshed["milestone_count"] == total + 1
        assert refreshed["completion_percentage"] == round(100 / (total + 1), 2)

    def test_complete_project_marks_every_milestone(self, client, auth_headers):
        project = client.get("/api/v1/projects", headers=auth_headers).json()[0]
        response = client.post(
            f"/api/v1/projects/{project['id']}/complete", headers=auth_headers
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "completed"
        assert body["completion_percentage"] == 100.0
        assert body["completed_milestones"] == body["milestone_count"]

    def test_checklist_items(self, client, auth_headers):
        project = client.get("/api/v1/projects", headers=auth_headers).json()[0]
        created = client.post(
            f"/api/v1/projects/{project['id']}/checklist",
            json={"title": "Write README"},
            headers=auth_headers,
        )
        assert created.status_code == 201
        item = created.json()
        assert item["is_done"] is False

        done = client.patch(
            f"/api/v1/projects/checklist/{item['id']}",
            json={"is_done": True},
            headers=auth_headers,
        )
        assert done.status_code == 200
        assert done.json()["is_done"] is True

        refreshed = client.get(f"/api/v1/projects/{project['id']}", headers=auth_headers).json()
        assert refreshed["completed_checklist_items"] == 1

        assert (
            client.delete(
                f"/api/v1/projects/checklist/{item['id']}", headers=auth_headers
            ).status_code
            == 204
        )
