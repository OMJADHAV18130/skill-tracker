"""Seed integrity tests - the curriculum must stay exactly as specified."""

from __future__ import annotations

from sqlalchemy import func, select

from app.db.seed import seed_shared_roadmap, seed_user_content
from app.db.seed_data import PROJECTS, RESOURCES, TOPICS
from app.models import Project, RoadmapPhase, Topic, TopicProgress, TopicResource


class TestSharedSeed:
    def test_expected_curriculum_is_present(self, db):
        assert db.scalar(select(func.count()).select_from(RoadmapPhase)) == 9
        assert db.scalar(select(func.count()).select_from(Topic)) == 93
        assert db.scalar(select(func.count()).select_from(TopicResource)) > 0
        assert len(RESOURCES) >= 14
        assert len(PROJECTS) == 6
        assert sum(len(topics) for topics in TOPICS.values()) == 93

    def test_phase_topics_are_ordered_and_complete(self, db):
        phases = db.scalars(select(RoadmapPhase).order_by(RoadmapPhase.order_index)).all()
        assert [phase.order_index for phase in phases] == list(range(1, 10))
        core_phases = [p for p in phases if p.track == "core"]
        dsa_phases = [p for p in phases if p.track == "dsa"]
        assert len(core_phases) == 7
        assert len(dsa_phases) == 2
        for phase in phases:
            topics = sorted(phase.topics, key=lambda topic: topic.order_index)
            assert topics
            assert [topic.order_index for topic in topics] == list(range(1, len(topics) + 1))
            assert all(topic.subtopics for topic in topics)

    def test_every_resource_url_is_https(self, db):
        from app.models import Resource

        for resource in db.scalars(select(Resource)).all():
            assert resource.url.startswith("https://"), resource.url
            assert resource.is_official is True

    def test_seeding_is_idempotent(self, db):
        before = (
            db.scalar(select(func.count()).select_from(RoadmapPhase)),
            db.scalar(select(func.count()).select_from(Topic)),
            db.scalar(select(func.count()).select_from(TopicResource)),
        )
        stats = seed_shared_roadmap(db)
        after = (
            db.scalar(select(func.count()).select_from(RoadmapPhase)),
            db.scalar(select(func.count()).select_from(Topic)),
            db.scalar(select(func.count()).select_from(TopicResource)),
        )
        assert stats == {"phases": 0, "topics": 0, "resources": 0, "links": 0}
        assert before == after


class TestDemoSeed:
    def test_demo_account_can_sign_in_and_has_activity(self, db, client):
        from app.core.config import settings
        from app.db.seed import ensure_demo_user, seed_demo_data
        from app.models import DailyTask

        demo = ensure_demo_user(db)
        assert demo is not None
        seed_demo_data(db, demo)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": settings.demo_user_email,
                "password": settings.demo_user_password,
            },
        )
        assert response.status_code == 200, response.text

        headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
        dashboard = client.get("/api/v1/dashboard", headers=headers).json()
        assert dashboard["completed_topics"] > 0
        assert dashboard["total_study_minutes"] > 0
        assert (
            db.scalar(
                select(func.count())
                .select_from(DailyTask)
                .where(DailyTask.user_id == demo.id)
            )
            > 0
        )


class TestUserSeed:
    def test_user_seed_creates_progress_and_projects_once(self, db, auth_user):
        import uuid as _uuid

        user_id = _uuid.UUID(auth_user["user"]["id"])
        from app.models import User

        user = db.get(User, user_id)
        assert user is not None

        progress = db.scalar(
            select(func.count())
            .select_from(TopicProgress)
            .where(TopicProgress.user_id == user.id)
        )
        projects = db.scalar(
            select(func.count()).select_from(Project).where(Project.user_id == user.id)
        )
        assert progress == 93
        assert projects == 6

        seed_user_content(db, user)
        db.flush()
        assert (
            db.scalar(
                select(func.count())
                .select_from(TopicProgress)
                .where(TopicProgress.user_id == user.id)
            )
            == 93
        )
        assert (
            db.scalar(
                select(func.count()).select_from(Project).where(Project.user_id == user.id)
            )
            == 6
        )

    def test_users_do_not_share_progress_rows(self, db, user_factory):
        import uuid as _uuid

        first = user_factory()
        second = user_factory()
        first_ids = set(
            db.scalars(
                select(TopicProgress.id).where(
                    TopicProgress.user_id == _uuid.UUID(first["user"]["id"])
                )
            ).all()
        )
        second_ids = set(
            db.scalars(
                select(TopicProgress.id).where(
                    TopicProgress.user_id == _uuid.UUID(second["user"]["id"])
                )
            ).all()
        )
        assert len(first_ids) == len(second_ids) == 93
        assert first_ids.isdisjoint(second_ids)
