"""Resource library tests."""

from __future__ import annotations


class TestSeededLibrary:
    def test_official_resources_are_listed(self, client, auth_headers):
        body = client.get("/api/v1/resources", headers=auth_headers).json()
        assert body["total"] >= 11
        assert body["bookmarked_count"] == 0
        titles = {item["title"] for item in body["items"]}
        assert "Spring Guides" in titles
        assert all(item["is_official"] for item in body["items"])

    def test_categories_endpoint(self, client, auth_headers):
        response = client.get("/api/v1/resources/categories", headers=auth_headers)
        assert response.status_code == 200
        categories = response.json()
        assert "Java" in categories
        assert "Docker" in categories
        assert categories == sorted(categories)

    def test_search_and_category_filter(self, client, auth_headers):
        by_query = client.get(
            "/api/v1/resources", params={"q": "spring"}, headers=auth_headers
        ).json()
        assert by_query["total"] >= 1
        assert all("spring" in (item["title"] + item["description"]).lower() for item in by_query["items"])

        by_category = client.get(
            "/api/v1/resources", params={"category": "docker"}, headers=auth_headers
        ).json()
        assert by_category["total"] >= 1
        assert all(item["category"].lower() == "docker" for item in by_category["items"])


class TestBookmarks:
    def test_bookmark_round_trip(self, client, auth_headers):
        resource = client.get("/api/v1/resources", headers=auth_headers).json()["items"][0]

        marked = client.put(
            f"/api/v1/resources/{resource['id']}/bookmark",
            json={"is_bookmarked": True},
            headers=auth_headers,
        )
        assert marked.status_code == 200
        assert marked.json()["is_bookmarked"] is True

        bookmarked = client.get(
            "/api/v1/resources", params={"bookmarked": True}, headers=auth_headers
        ).json()
        assert bookmarked["total"] == 1
        assert bookmarked["bookmarked_count"] == 1
        assert bookmarked["items"][0]["id"] == resource["id"]

        unmarked = client.put(
            f"/api/v1/resources/{resource['id']}/bookmark",
            json={"is_bookmarked": False},
            headers=auth_headers,
        )
        assert unmarked.json()["is_bookmarked"] is False
        assert (
            client.get(
                "/api/v1/resources", params={"bookmarked": True}, headers=auth_headers
            ).json()["total"]
            == 0
        )

    def test_bookmarking_is_per_user(self, client, auth_headers, user_factory):
        other = user_factory()
        resource = client.get("/api/v1/resources", headers=auth_headers).json()["items"][0]
        client.put(
            f"/api/v1/resources/{resource['id']}/bookmark",
            json={"is_bookmarked": True},
            headers=auth_headers,
        )
        theirs = client.get("/api/v1/resources", headers=other["headers"]).json()
        assert theirs["bookmarked_count"] == 0
        assert theirs["items"][0]["is_bookmarked"] is False


class TestCustomResources:
    def test_create_link_and_delete(self, client, auth_headers):
        topic = client.get("/api/v1/roadmap/phases", headers=auth_headers).json()["items"][0][
            "topics"
        ][0]

        created = client.post(
            "/api/v1/resources",
            json={
                "title": "My Spring notes",
                "url": "https://example.com/spring-notes",
                "description": "Personal summary",
                "category": "Spring Boot",
                "tags": ["notes"],
                "linked_topic_id": topic["id"],
            },
            headers=auth_headers,
        )
        assert created.status_code == 201, created.text
        resource = created.json()
        assert resource["is_official"] is False
        assert resource["linked_topic_title"] == topic["title"]

        updated = client.patch(
            f"/api/v1/resources/{resource['id']}",
            json={"title": "My Spring notes v2"},
            headers=auth_headers,
        )
        assert updated.status_code == 200
        assert updated.json()["title"] == "My Spring notes v2"

        assert (
            client.delete(f"/api/v1/resources/{resource['id']}", headers=auth_headers).status_code
            == 204
        )
        assert (
            client.get(f"/api/v1/resources/{resource['id']}", headers=auth_headers).status_code
            == 404
        )

    def test_custom_resources_are_private(self, client, auth_headers, user_factory):
        other = user_factory()
        created = client.post(
            "/api/v1/resources",
            json={
                "title": "Private notes",
                "url": "https://example.com/private",
                "category": "Java",
            },
            headers=auth_headers,
        ).json()

        other_items = client.get("/api/v1/resources", headers=other["headers"]).json()["items"]
        assert all(item["id"] != created["id"] for item in other_items)
        assert (
            client.get(
                f"/api/v1/resources/{created['id']}", headers=other["headers"]
            ).status_code
            == 404
        )
        assert (
            client.patch(
                f"/api/v1/resources/{created['id']}",
                json={"title": "Hijacked"},
                headers=other["headers"],
            ).status_code
            == 404
        )

    def test_official_resources_are_read_only(self, client, auth_headers):
        resource = client.get("/api/v1/resources", headers=auth_headers).json()["items"][0]
        assert (
            client.patch(
                f"/api/v1/resources/{resource['id']}",
                json={"title": "Hacked"},
                headers=auth_headers,
            ).status_code
            == 403
        )
        assert (
            client.delete(f"/api/v1/resources/{resource['id']}", headers=auth_headers).status_code
            == 403
        )

    def test_url_validation(self, client, auth_headers):
        response = client.post(
            "/api/v1/resources",
            json={"title": "Bad", "url": "javascript:alert(1)", "category": "Java"},
            headers=auth_headers,
        )
        assert response.status_code == 422
