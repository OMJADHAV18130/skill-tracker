"""Preferences, export/import and reset tests."""

from __future__ import annotations


def complete_first_topic(client, headers) -> dict:
    topic = client.get("/api/v1/roadmap/phases", headers=headers).json()["items"][0]["topics"][0]
    response = client.patch(
        f"/api/v1/roadmap/topics/{topic['id']}/progress",
        json={"status": "completed", "rating": 5},
        headers=headers,
    )
    assert response.status_code == 200
    return topic


class TestPreferences:
    def test_defaults(self, client, auth_headers):
        body = client.get("/api/v1/settings", headers=auth_headers).json()
        assert body["daily_goal_minutes"] == 120
        assert body["theme"] == "system"
        assert body["phase_durations"] == {}
        assert body["reminders_enabled"] is False

    def test_update_and_persist(self, client, auth_headers):
        response = client.patch(
            "/api/v1/settings",
            json={
                "daily_goal_minutes": 90,
                "theme": "dark",
                "timezone": "Asia/Kolkata",
                "reminders_enabled": True,
                "reminder_time": "20:30:00",
                "phase_durations": {"phase-1": 2},
            },
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        body = client.get("/api/v1/settings", headers=auth_headers).json()
        assert body["daily_goal_minutes"] == 90
        assert body["theme"] == "dark"
        assert body["timezone"] == "Asia/Kolkata"
        assert body["reminders_enabled"] is True
        assert body["reminder_time"].startswith("20:30")
        assert body["phase_durations"] == {"phase-1": 2}

    def test_goal_bounds_are_validated(self, client, auth_headers):
        assert (
            client.patch(
                "/api/v1/settings", json={"daily_goal_minutes": 10}, headers=auth_headers
            ).status_code
            == 422
        )
        assert (
            client.patch(
                "/api/v1/settings", json={"daily_goal_minutes": 481}, headers=auth_headers
            ).status_code
            == 422
        )
        assert (
            client.patch(
                "/api/v1/settings",
                json={"phase_durations": {"phase-1": 0}},
                headers=auth_headers,
            ).status_code
            == 422
        )


class TestExport:
    def test_json_export_contains_every_section(self, client, auth_headers):
        complete_first_topic(client, auth_headers)
        response = client.get("/api/v1/settings/export.json", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        assert "attachment" in response.headers["content-disposition"]
        payload = response.json()
        assert payload["schema_version"] == "1.0"
        assert payload["user"]["email"]
        assert len(payload["topic_progress"]) == 93
        assert payload["preferences"]["daily_goal_minutes"] == 120
        assert payload["projects"]

    def test_csv_export_has_a_header_and_rows(self, client, auth_headers):
        complete_first_topic(client, auth_headers)
        response = client.get("/api/v1/settings/export.csv", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        lines = response.text.strip().splitlines()
        assert lines[0].startswith("topic_slug,topic_title,status")
        assert len(lines) == 1 + 93  # header + all topic rows


class TestImport:
    def test_validate_reports_counts_and_errors(self, client, auth_headers):
        export = client.get("/api/v1/settings/export.json", headers=auth_headers).json()
        valid = client.post(
            "/api/v1/settings/import/validate", json=export, headers=auth_headers
        )
        assert valid.status_code == 200
        assert valid.json()["valid"] is True
        assert valid.json()["counts"]["topic_progress"] == 93

        export["topic_progress"][0]["status"] = "banana"
        export["study_sessions"].append({"minutes": -5, "session_date": "2026-01-01"})
        invalid = client.post(
            "/api/v1/settings/import/validate", json=export, headers=auth_headers
        ).json()
        assert invalid["valid"] is False
        assert any("invalid status" in error for error in invalid["errors"])
        assert any("invalid duration" in error for error in invalid["errors"])

    def test_import_requires_confirmation(self, client, auth_headers):
        export = client.get("/api/v1/settings/export.json", headers=auth_headers).json()
        response = client.post(
            "/api/v1/settings/import",
            json={"payload": export, "confirm": False},
            headers=auth_headers,
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "confirmation_required"

    def test_export_reset_import_round_trip(self, client, auth_headers):
        topic = complete_first_topic(client, auth_headers)
        export = client.get("/api/v1/settings/export.json", headers=auth_headers).json()

        reset = client.post(
            "/api/v1/settings/reset", params={"confirm": True}, headers=auth_headers
        )
        assert reset.status_code == 200
        after_reset = client.get("/api/v1/roadmap/phases", headers=auth_headers).json()
        assert after_reset["completed_topics"] == 0
        assert len(client.get("/api/v1/projects", headers=auth_headers).json()) == 6

        imported = client.post(
            "/api/v1/settings/import",
            json={"payload": export, "confirm": True, "mode": "replace"},
            headers=auth_headers,
        )
        assert imported.status_code == 200, imported.text

        restored = client.get("/api/v1/roadmap/phases", headers=auth_headers).json()
        assert restored["completed_topics"] == 1
        restored_topic = restored["items"][0]["topics"][0]
        assert restored_topic["id"] == topic["id"]
        assert restored_topic["progress"]["rating"] == 5


class TestReset:
    def test_reset_clears_personal_data_but_keeps_library(self, client, auth_headers):
        complete_first_topic(client, auth_headers)
        client.post(
            "/api/v1/planner/tasks",
            json={"title": "Task", "task_date": "2026-02-01"},
            headers=auth_headers,
        )
        client.post(
            "/api/v1/planner/sessions",
            json={"minutes": 30, "session_date": "2026-02-01"},
            headers=auth_headers,
        )

        response = client.post(
            "/api/v1/settings/reset", params={"confirm": True}, headers=auth_headers
        )
        assert response.status_code == 200

        assert client.get("/api/v1/planner/tasks", headers=auth_headers).json()["meta"][
            "total"
        ] == 0
        assert client.get("/api/v1/roadmap/phases", headers=auth_headers).json()[
            "completed_topics"
        ] == 0
        assert client.get("/api/v1/resources", headers=auth_headers).json()["total"] >= 11
        projects = client.get("/api/v1/projects", headers=auth_headers).json()
        assert len(projects) == 6
        assert all(p["status"] == "not_started" for p in projects)

    def test_reset_requires_confirmation(self, client, auth_headers):
        response = client.post("/api/v1/settings/reset", headers=auth_headers)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "confirmation_required"
