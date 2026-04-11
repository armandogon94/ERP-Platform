import pytest
from django.test import override_settings


@pytest.mark.django_db
class TestAPIRoot:
    """Smoke tests: Django serves the API root and health check."""

    def test_api_root_returns_200(self, api_client):
        response = api_client.get("/api/v1/")
        assert response.status_code == 200

    def test_api_root_contains_version(self, api_client):
        response = api_client.get("/api/v1/")
        data = response.json()
        assert data["name"] == "ERP Platform API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "ok"

    def test_swagger_schema_returns_200(self, api_client):
        response = api_client.get("/api/schema/")
        assert response.status_code == 200

    def test_nonexistent_endpoint_returns_404(self, api_client):
        response = api_client.get("/api/v1/nonexistent/")
        assert response.status_code == 404
