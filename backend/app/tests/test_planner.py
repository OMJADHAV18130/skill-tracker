"""Daily planner, study sessions, streak and calendar tests."""

from __future__ import annotations

from datetime import date, timedelta

TODAY = date.today()


def iso(offset: int = 0) -> str:
    return (TODAY + timedelta(days=offset)).isoformat()


class TestTaskCrud:
    def test_create_list_update_delete(self, client, auth_headers):
        created = client.post(
            "/api/v1/planner/tasks",
            json={
                "title": "Study JPA",
                "description": "Chapters 1-3",
                "task_date": iso(),
                "category": "Spring Boot",
                "estimated_minutes": 60,
                "priority": "high",
            },
            headers=auth_headers,
        )
        assert created.status_code == 201
        task = created.json()
        assert task["is_completed"] is False
        assert task["priority"] == "high"

        listed = client.get("/api/v1/planner/tasks", headers=auth_headers).json()
        assert listed["meta"]["total"] == 1
        assert listed["items"][0]["id"] == task["id"]

        updated = client.patch(
            f"/api/v1/planner/tasks/{task['id']}",
            json={"title": "Study JPA deeply", "estimated_minutes": 90},
            headers=auth_headers,
        )
        assert updated.status_code == 200
        assert updated.json()["title"] == "Study JPA deeply"

        deleted = client.delete(f"/api/v1/planner/tasks/{task['id']}", headers=auth_headers)
        assert deleted.status_code == 204
        assert client.get("/api/v1/planner/tasks", headers=auth_headers).json()["meta"]["total"] == 0

    def test_filter_by_date_and_completion(self, client, auth_headers):
        client.post(
            "/api/v1/planner/tasks",
            json={"title": "Old", "task_date": iso(-3)},
            headers=auth_headers,
        )
        today_task = client.post(
            "/api/v1/planner/tasks",
            json={"title": "Today", "task_date": iso()},
            headers=auth_headers,
        ).json()
        client.patch(
            f"/api/v1/planner/tasks/{today_task['id']}/completion",
            json={"is_completed": True},
            headers=auth_headers,
        )

        today_only = client.get(
            f"/api/v1/planner/tasks?start={iso()}&end={iso()}", headers=auth_headers
        ).json()
        assert today_only["meta"]["total"] == 1

        completed = client.get(
            "/api/v1/planner/tasks?is_completed=true", headers=auth_headers
        ).json()
        assert completed["meta"]["total"] == 1
        assert completed["items"][0]["title"] == "Today"

    def test_validation_rejects_negative_minutes(self, client, auth_headers):
        response = client.post(
            "/api/v1/planner/tasks",
            json={"title": "Bad", "task_date": iso(), "estimated_minutes": -30},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestCompletion:
    def test_mark_complete_sets_timestamp(self, client, auth_headers):
        task = client.post(
            "/api/v1/planner/tasks",
            json={"title": "Finish chapter", "task_date": iso()},
            headers=auth_headers,
        ).json()
        response = client.patch(
            f"/api/v1/planner/tasks/{task['id']}/completion",
            json={"is_completed": True},
            headers=auth_headers,
        ).json()
        assert response["is_completed"] is True
        assert response["completed_at"] is not None

        reopened = client.patch(
            f"/api/v1/planner/tasks/{task['id']}/completion",
            json={"is_completed": False},
            headers=auth_headers,
        ).json()
        assert reopened["is_completed"] is False
        assert reopened["completed_at"] is None


class TestStudyLogging:
    def test_log_time_records_actual_minutes(self, client, auth_headers):
        task = client.post(
            "/api/v1/planner/tasks",
            json={"title": "Practice SQL", "task_date": iso(), "estimated_minutes": 45},
            headers=auth_headers,
        ).json()

        response = client.post(
            f"/api/v1/planner/tasks/{task['id']}/log",
            json={"actual_minutes": 50, "session_note": "Went longer", "completed": True},
            headers=auth_headers,
        ).json()
        assert response["actual_minutes"] == 50
        assert response["session_note"] == "Went longer"
        assert response["is_completed"] is True

    def test_study_hours_sum_sessions(self, client, auth_headers):
        client.post(
            "/api/v1/planner/sessions",
            json={"minutes": 30, "session_date": iso()},
            headers=auth_headers,
        )
        client.post(
            "/api/v1/planner/sessions",
            json={"minutes": 90, "session_date": iso()},
            headers=auth_headers,
        )
        day = client.get(f"/api/v1/planner/day?date={iso()}", headers=auth_headers).json()
        assert day["summary"]["logged_minutes"] == 120

    def test_relogging_time_updates_one_session(self, client, auth_headers):
        task = client.post(
            "/api/v1/planner/tasks",
            json={"title": "Refactor service", "task_date": iso(), "estimated_minutes": 60},
            headers=auth_headers,
        ).json()

        client.post(
            f"/api/v1/planner/tasks/{task['id']}/log",
            json={"actual_minutes": 20},
            headers=auth_headers,
        )
        client.post(
            f"/api/v1/planner/tasks/{task['id']}/log",
            json={"actual_minutes": 45, "session_note": "Corrected"},
            headers=auth_headers,
        )

        sessions = client.get("/api/v1/planner/sessions", headers=auth_headers).json()
        assert len(sessions) == 1
        assert sessions[0]["minutes"] == 45
        assert sessions[0]["note"] == "Corrected"

        dashboard = client.get("/api/v1/dashboard", headers=auth_headers).json()
        assert dashboard["total_study_minutes"] == 45

    def test_session_minutes_must_be_positive(self, client, auth_headers):
        response = client.post(
            "/api/v1/planner/sessions",
            json={"minutes": 0, "session_date": iso()},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestDayPlan:
    def test_day_summary_compares_planned_and_completed(self, client, auth_headers):
        task = client.post(
            "/api/v1/planner/tasks",
            json={"title": "Plan", "task_date": iso(), "estimated_minutes": 60},
            headers=auth_headers,
        ).json()
        client.patch(
            f"/api/v1/planner/tasks/{task['id']}/completion",
            json={"is_completed": True},
            headers=auth_headers,
        )
        client.post(
            f"/api/v1/planner/tasks/{task['id']}/log",
            json={"actual_minutes": 55},
            headers=auth_headers,
        )

        day = client.get(f"/api/v1/planner/day?date={iso()}", headers=auth_headers).json()
        assert day["summary"]["planned_tasks"] == 1
        assert day["summary"]["completed_tasks"] == 1
        assert day["summary"]["planned_minutes"] == 60
        assert day["summary"]["completed_minutes"] == 55
        assert day["goal_minutes"] == 120

    def test_carry_forward_creates_new_task(self, client, auth_headers):
        task = client.post(
            "/api/v1/planner/tasks",
            json={"title": "Unfinished", "task_date": iso(-1)},
            headers=auth_headers,
        ).json()
        response = client.post(
            f"/api/v1/planner/tasks/{task['id']}/carry-forward",
            json={"target_date": iso(), "delete_original": True},
            headers=auth_headers,
        )
        assert response.status_code == 201
        carried = response.json()
        assert carried["task_date"] == iso()
        assert carried["carried_from_id"] == task["id"]
        assert client.get(f"/api/v1/planner/tasks/{task['id']}", headers=auth_headers).status_code == 404

    def test_completed_task_cannot_be_carried_forward(self, client, auth_headers):
        task = client.post(
            "/api/v1/planner/tasks",
            json={"title": "Done", "task_date": iso()},
            headers=auth_headers,
        ).json()
        client.patch(
            f"/api/v1/planner/tasks/{task['id']}/completion",
            json={"is_completed": True},
            headers=auth_headers,
        )
        response = client.post(
            f"/api/v1/planner/tasks/{task['id']}/carry-forward",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "task_completed"


class TestCalendarAndStreak:
    def test_calendar_returns_every_day_of_month(self, client, auth_headers):
        body = client.get(
            f"/api/v1/planner/calendar?year={TODAY.year}&month={TODAY.month}",
            headers=auth_headers,
        ).json()
        assert body["month"] == f"{TODAY.year:04d}-{TODAY.month:02d}"
        assert len(body["days"]) >= 28
        assert body["total_minutes"] == 0

    def test_calendar_aggregates_minutes(self, client, auth_headers):
        client.post(
            "/api/v1/planner/sessions",
            json={"minutes": 45, "session_date": iso()},
            headers=auth_headers,
        )
        body = client.get(
            f"/api/v1/planner/calendar?year={TODAY.year}&month={TODAY.month}",
            headers=auth_headers,
        ).json()
        today_entry = next(d for d in body["days"] if d["date"] == iso())
        assert today_entry["total_minutes"] == 45
        assert today_entry["has_activity"] is True

    def test_streak_counts_consecutive_days(self, client, auth_headers):
        for offset in (0, -1, -2):
            client.post(
                "/api/v1/planner/sessions",
                json={"minutes": 30, "session_date": iso(offset)},
                headers=auth_headers,
            )
        streak = client.get("/api/v1/planner/streak", headers=auth_headers).json()
        assert streak["current_streak"] == 3
        assert streak["longest_streak"] == 3
        assert streak["total_active_days"] == 3

    def test_streak_breaks_on_a_gap(self, client, auth_headers):
        for offset in (0, -1, -3):
            client.post(
                "/api/v1/planner/sessions",
                json={"minutes": 30, "session_date": iso(offset)},
                headers=auth_headers,
            )
        streak = client.get("/api/v1/planner/streak", headers=auth_headers).json()
        assert streak["current_streak"] == 2
        assert streak["longest_streak"] == 2

    def test_zero_streak_with_no_activity(self, client, auth_headers):
        streak = client.get("/api/v1/planner/streak", headers=auth_headers).json()
        assert streak["current_streak"] == 0
        assert streak["longest_streak"] == 0

    def test_week_summary(self, client, auth_headers):
        client.post(
            "/api/v1/planner/sessions",
            json={"minutes": 60, "session_date": iso()},
            headers=auth_headers,
        )
        body = client.get("/api/v1/planner/week", headers=auth_headers).json()
        assert body["total_minutes"] == 60
        assert body["total_hours"] == 1.0
        assert len(body["daily_minutes"]) == 7
