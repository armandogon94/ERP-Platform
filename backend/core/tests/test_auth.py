import pytest
from django.contrib.auth.models import User

from core.factories import CompanyFactory, UserFactory
from core.models import Industry


@pytest.mark.django_db
class TestLogin:
    def test_login_returns_tokens_and_user(self, api_client):
        company = CompanyFactory(
            name="NovaPay",
            slug="novapay",
            brand_color="#2563EB",
            industry=Industry.FINTECH,
        )
        UserFactory(
            username="admin",
            email="admin@novapay.com",
            company=company,
        )
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "admin@novapay.com", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert data["user"]["email"] == "admin@novapay.com"
        assert data["company"]["name"] == "NovaPay"
        assert data["company"]["brand_color"] == "#2563EB"
        assert data["company"]["industry"] == "fintech"

    def test_login_invalid_credentials_returns_401(self, api_client):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "wrong@example.com", "password": "wrong"},
            format="json",
        )
        assert response.status_code == 401

    def test_login_missing_fields_returns_400(self, api_client):
        response = api_client.post(
            "/api/v1/auth/login/",
            {},
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestTokenRefresh:
    def test_refresh_returns_new_access_token(self, api_client):
        company = CompanyFactory()
        UserFactory(username="user1", email="user1@test.com", company=company)

        login = api_client.post(
            "/api/v1/auth/login/",
            {"email": "user1@test.com", "password": "testpass123"},
            format="json",
        )
        refresh_token = login.json()["refresh"]

        response = api_client.post(
            "/api/v1/auth/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.json()

    def test_refresh_invalid_token_returns_401(self, api_client):
        response = api_client.post(
            "/api/v1/auth/refresh/",
            {"refresh": "invalid-token"},
            format="json",
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestLogout:
    def test_logout_blacklists_refresh_token(self, api_client):
        company = CompanyFactory()
        UserFactory(username="user2", email="user2@test.com", company=company)

        login = api_client.post(
            "/api/v1/auth/login/",
            {"email": "user2@test.com", "password": "testpass123"},
            format="json",
        )
        tokens = login.json()
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = api_client.post(
            "/api/v1/auth/logout/",
            {"refresh": tokens["refresh"]},
            format="json",
        )
        assert response.status_code == 200

        # Refresh should now fail (token blacklisted)
        response = api_client.post(
            "/api/v1/auth/refresh/",
            {"refresh": tokens["refresh"]},
            format="json",
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestProtectedEndpoint:
    def test_unauthenticated_request_to_protected_endpoint(self, api_client):
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 401

    def test_authenticated_request_returns_user_info(self, api_client):
        company = CompanyFactory(name="TestCo", slug="testco")
        UserFactory(
            username="me",
            email="me@test.com",
            first_name="Jane",
            last_name="Smith",
            company=company,
        )

        login = api_client.post(
            "/api/v1/auth/login/",
            {"email": "me@test.com", "password": "testpass123"},
            format="json",
        )
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}"
        )

        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@test.com"
        assert data["first_name"] == "Jane"
        assert data["company"]["name"] == "TestCo"
