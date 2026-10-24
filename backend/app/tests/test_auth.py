"""Authentication, token lifecycle and account security tests."""

from __future__ import annotations

import pytest


class TestRegistration:
    def test_register_returns_tokens_and_user(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "New.Learner@Example.com",
                "username": "newlearner",
                "full_name": "New Learner",
                "password": "SuperSecret123",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["user"]["email"] == "new.learner@example.com"  # normalised
        assert "hashed_password" not in body["user"]
        assert body["user"]["role"] == "user"

    def test_password_is_hashed_not_stored_plaintext(self, client, db):
        from app.models.user import User

        client.post(
            "/api/v1/auth/register",
            json={
                "email": "hash@example.com",
                "username": "hashcheck",
                "password": "PlaintextPass1",
            },
        )
        user = db.query(User).filter(User.email == "hash@example.com").one()
        assert user.hashed_password != "PlaintextPass1"
        assert user.hashed_password.startswith("$2b$")

    def test_duplicate_email_is_rejected(self, client, auth_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": auth_user["payload"]["email"],
                "username": "unique-name",
                "password": "SuperSecret123",
            },
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "email_taken"

    def test_duplicate_username_is_rejected(self, client, auth_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "another@example.com",
                "username": auth_user["payload"]["username"],
                "password": "SuperSecret123",
            },
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "username_taken"

    @pytest.mark.parametrize(
        "payload",
        [
            {"email": "not-an-email", "username": "abc", "password": "SuperSecret123"},
            {"email": "ok@example.com", "username": "ab", "password": "SuperSecret123"},
            {"email": "ok@example.com", "username": "validname", "password": "short"},
            {"email": "ok@example.com", "username": "bad name!", "password": "SuperSecret123"},
        ],
    )
    def test_validation_errors_use_uniform_shape(self, client, payload):
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422
        body = response.json()
        assert body["error"]["code"] == "validation_error"
        assert body["error"]["details"]["errors"]


class TestLogin:
    def test_login_success(self, client, auth_user):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": auth_user["payload"]["email"],
                "password": auth_user["payload"]["password"],
            },
        )
        assert response.status_code == 200
        assert response.json()["access_token"]

    def test_login_is_case_insensitive_for_email(self, client, auth_user):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": auth_user["payload"]["email"].upper(),
                "password": auth_user["payload"]["password"],
            },
        )
        assert response.status_code == 200

    def test_wrong_password_is_rejected(self, client, auth_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": auth_user["payload"]["email"], "password": "wrong-password"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "invalid_credentials"

    def test_unknown_email_is_rejected(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "whatever123"},
        )
        assert response.status_code == 401
        # Same message as a wrong password - no account enumeration.
        assert response.json()["error"]["message"] == "Incorrect email or password"


class TestProtectedRoutes:
    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/auth/me",
            "/api/v1/dashboard",
            "/api/v1/roadmap/phases",
            "/api/v1/planner/tasks",
            "/api/v1/projects",
            "/api/v1/resources",
            "/api/v1/settings",
        ],
    )
    def test_requires_authentication(self, client, path):
        response = client.get(path)
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "missing_token"

    def test_rejects_garbage_token(self, client):
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer not.a.token"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "invalid_token"

    def test_rejects_refresh_token_as_access_token(self, client, auth_user):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_user['tokens']['refresh_token']}"},
        )
        assert response.status_code == 401

    def test_me_returns_the_token_subject(self, client, auth_user):
        response = client.get("/api/v1/auth/me", headers=auth_user["headers"])
        assert response.status_code == 200
        assert response.json()["id"] == auth_user["user"]["id"]


class TestTokenLifecycle:
    def test_refresh_rotates_the_refresh_token(self, client, auth_user):
        original = auth_user["tokens"]["refresh_token"]
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": original})
        assert response.status_code == 200
        body = response.json()
        assert body["refresh_token"] != original

        # The old refresh token is now revoked.
        reused = client.post("/api/v1/auth/refresh", json={"refresh_token": original})
        assert reused.status_code == 401

    def test_new_access_token_works(self, client, auth_user):
        refreshed = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": auth_user["tokens"]["refresh_token"]}
        ).json()
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refreshed['access_token']}"},
        )
        assert response.status_code == 200

    def test_logout_revokes_refresh_token(self, client, auth_user):
        refresh_token = auth_user["tokens"]["refresh_token"]
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers=auth_user["headers"],
        )
        assert response.status_code == 200
        retry = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert retry.status_code == 401

    def test_invalid_refresh_token(self, client):
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "x" * 40})
        assert response.status_code == 401


class TestPasswordChange:
    def test_wrong_current_password_is_rejected(self, client, auth_user):
        response = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "nope", "new_password": "BrandNewPass1"},
            headers=auth_user["headers"],
        )
        assert response.status_code == 401

    def test_password_change_revokes_sessions_and_updates_login(self, client, auth_user):
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": auth_user["payload"]["password"],
                "new_password": "BrandNewPass1",
            },
            headers=auth_user["headers"],
        )
        assert response.status_code == 200

        old_login = client.post(
            "/api/v1/auth/login",
            json={
                "email": auth_user["payload"]["email"],
                "password": auth_user["payload"]["password"],
            },
        )
        assert old_login.status_code == 401

        new_login = client.post(
            "/api/v1/auth/login",
            json={"email": auth_user["payload"]["email"], "password": "BrandNewPass1"},
        )
        assert new_login.status_code == 200

        # All refresh tokens were revoked.
        assert (
            client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": auth_user["tokens"]["refresh_token"]},
            ).status_code
            == 401
        )

    def test_update_profile(self, client, auth_user):
        response = client.patch(
            "/api/v1/auth/me",
            json={"full_name": "Renamed Learner"},
            headers=auth_user["headers"],
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Renamed Learner"
