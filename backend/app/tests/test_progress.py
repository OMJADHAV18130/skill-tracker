"""Progress calculation tests - no hardcoded numbers anywhere."""

from __future__ import annotations

from datetime import date


class TestRoadmapProgress:
    def test_all_topics_start_at_zero(self, client, auth_user):
        response = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"])
        assert response.status_code == 200
        body = response.json()
        assert body["completed_topics"] == 0
        assert body["completion_percentage"] == 0.0
        assert body["total_topics"] == 69
        assert len(body["items"]) == 7
        for phase in body["items"]:
            assert phase["completed_count"] == 0
            assert phase["completion_percentage"] == 0.0
            assert phase["status"] == "not_started"

    def test_completing_a_topic_updates_phase_and_overall(self, client, auth_user):
        phases = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        phase = phases["items"][0]
        topic = phase["topics"][0]
        topic_count = phase["topic_count"]

        client.patch(
            f"/api/v1/roadmap/topics/{topic['id']}/progress",
            json={"status": "completed"},
            headers=auth_user["headers"],
        )

        refreshed = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        refreshed_phase = refreshed["items"][0]
        assert refreshed_phase["completed_count"] == 1
        assert refreshed_phase["completion_percentage"] == round(100 / topic_count, 2)
        assert refreshed["completed_topics"] == 1
        assert refreshed["completion_percentage"] == round(100 / 69, 2)
        assert refreshed_phase["status"] == "in_progress"

    def test_marking_in_progress_does_not_count_as_completed(self, client, auth_user):
        phases = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        topic = phases["items"][0]["topics"][0]

        response = client.patch(
            f"/api/v1/roadmap/topics/{topic['id']}/progress",
            json={"status": "in_progress"},
            headers=auth_user["headers"],
        ).json()
        assert response["progress"]["status"] == "in_progress"
        assert response["progress"]["started_at"] is not None
        assert response["progress"]["completed_at"] is None

        refreshed = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        assert refreshed["completed_topics"] == 0
        assert refreshed["items"][0]["in_progress_count"] == 1
        assert refreshed["items"][0]["status"] == "in_progress"

    def test_reopen_and_recomplete_never_double_counts(self, client, auth_user):
        phases = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        topic_id = phases["items"][0]["topics"][0]["id"]
        url = f"/api/v1/roadmap/topics/{topic_id}/progress"

        first = client.patch(url, json={"status": "completed"}, headers=auth_user["headers"]).json()
        first_completed_at = first["progress"]["completed_at"]
        assert first_completed_at is not None

        # Re-completing an already completed topic is idempotent.
        second = client.patch(url, json={"status": "completed"}, headers=auth_user["headers"]).json()
        assert second["progress"]["completed_at"] == first_completed_at

        after_repeat = client.get(
            "/api/v1/roadmap/phases", headers=auth_user["headers"]
        ).json()
        assert after_repeat["completed_topics"] == 1
        assert after_repeat["completion_percentage"] == round(100 / 69, 2)

        # Re-open, then complete again - still exactly one completed topic.
        client.patch(url, json={"status": "not_started"}, headers=auth_user["headers"])
        reopened = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        assert reopened["completed_topics"] == 0

        client.patch(url, json={"status": "completed"}, headers=auth_user["headers"])
        again = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        assert again["completed_topics"] == 1
        assert again["completion_percentage"] == round(100 / 69, 2)

    def test_complete_whole_phase(self, client, auth_user):
        phases = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        phase = phases["items"][0]
        for topic in phase["topics"]:
            client.patch(
                f"/api/v1/roadmap/topics/{topic['id']}/progress",
                json={"status": "completed"},
                headers=auth_user["headers"],
            )
        refreshed = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        assert refreshed["items"][0]["status"] == "completed"
        assert refreshed["items"][0]["completion_percentage"] == 100.0
        assert refreshed["completed_topics"] == phase["topic_count"]

    def test_rating_and_priority_are_persisted(self, client, auth_user):
        phases = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        topic_id = phases["items"][0]["topics"][0]["id"]
        response = client.patch(
            f"/api/v1/roadmap/topics/{topic_id}/progress",
            json={"status": "completed", "rating": 5, "priority": "high"},
            headers=auth_user["headers"],
        ).json()
        assert response["progress"]["rating"] == 5
        assert response["progress"]["priority"] == "high"

    def test_invalid_rating_is_rejected(self, client, auth_user):
        phases = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        topic_id = phases["items"][0]["topics"][0]["id"]
        response = client.patch(
            f"/api/v1/roadmap/topics/{topic_id}/progress",
            json={"rating": 9},
            headers=auth_user["headers"],
        )
        assert response.status_code == 422


class TestDashboard:
    def test_zero_state_dashboard(self, client, auth_user):
        response = client.get("/api/v1/dashboard", headers=auth_user["headers"])
        assert response.status_code == 200
        body = response.json()
        assert body["overall_completion_percentage"] == 0
        assert body["completed_topics"] == 0
        assert body["total_topics"] == 69
        assert body["total_study_hours"] == 0
        assert body["current_streak"] == 0
        assert len(body["weekly_study"]) == 7
        assert len(body["phase_progress"]) == 7
        assert body["projects_total"] == 6
        assert body["todays_tasks"] == []
        # Next recommendation points at the very first topic.
        assert body["next_recommended_topic"]["status"] == "not_started"

    def test_dashboard_reflects_completion(self, client, auth_user):
        phases = client.get("/api/v1/roadmap/phases", headers=auth_user["headers"]).json()
        first = phases["items"][0]["topics"][0]
        second = phases["items"][0]["topics"][1]
        for topic in (first, second):
            client.patch(
                f"/api/v1/roadmap/topics/{topic['id']}/progress",
                json={"status": "completed"},
                headers=auth_user["headers"],
            )

        body = client.get("/api/v1/dashboard", headers=auth_user["headers"]).json()
        assert body["completed_topics"] == 2
        assert body["overall_completion_percentage"] == round(2 / 69 * 100, 2)
        # The next recommendation is the first *unfinished* topic.
        assert body["next_recommended_topic"]["id"] == phases["items"][0]["topics"][2]["id"]
        assert body["phase_progress"][0]["completed_topics"] == 2

    def test_study_hours_come_from_sessions_only(self, client, auth_user):
        today = date.today().isoformat()
        # A task with logged minutes but no session must not count.
        client.post(
            "/api/v1/planner/tasks",
            json={"title": "No session", "task_date": today, "actual_minutes": 90},
            headers=auth_user["headers"],
        )
        body = client.get("/api/v1/dashboard", headers=auth_user["headers"]).json()
        assert body["total_study_minutes"] == 0

        client.post(
            "/api/v1/planner/sessions",
            json={"minutes": 120, "session_date": today},
            headers=auth_user["headers"],
        )
        body = client.get("/api/v1/dashboard", headers=auth_user["headers"]).json()
        assert body["total_study_minutes"] == 120
        assert body["total_study_hours"] == 2.0

    def test_dashboard_shows_today_tasks_and_goal_percentage(self, client, auth_user):
        today = date.today().isoformat()
        client.post(
            "/api/v1/planner/tasks",
            json={
                "title": "Today's work",
                "task_date": today,
                "estimated_minutes": 60,
                "actual_minutes": 60,
            },
            headers=auth_user["headers"],
        )
        client.post(
            "/api/v1/planner/sessions",
            json={"minutes": 60, "session_date": today},
            headers=auth_user["headers"],
        )
        body = client.get("/api/v1/dashboard", headers=auth_user["headers"]).json()
        assert len(body["todays_tasks"]) == 1
        assert body["todays_planned_minutes"] == 60
        assert body["todays_goal_minutes"] == 120  # default goal
        assert body["todays_goal_percentage"] == 50.0
