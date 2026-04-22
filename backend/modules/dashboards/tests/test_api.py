"""HTTP tests for the Dashboards REST surface."""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.dashboards.models import Dashboard, DashboardWidget


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestDashboardAutoSeed:
    def test_list_lazily_seeds_default_for_new_company(self, api_client):
        """First GET on an empty tenant creates the default dashboard."""
        company = CompanyFactory(industry="fintech")
        user = UserFactory(company=company)
        auth(api_client, user)
        assert Dashboard.objects.filter(company=company).count() == 0

        response = api_client.get("/api/v1/dashboards/dashboards/")
        assert response.status_code == 200
        assert Dashboard.objects.filter(company=company).count() == 1

        body = response.json()
        assert len(body) == 1
        assert body[0]["is_default"] is True
        # Fintech preset has 8 widgets
        assert len(body[0]["widgets"]) == 8

    def test_default_action_returns_the_default_dashboard(self, api_client):
        company = CompanyFactory(industry="dental")
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.get("/api/v1/dashboards/dashboards/default/")
        assert response.status_code == 200
        body = response.json()
        assert body["is_default"] is True
        assert body["industry_preset"] == "dental"

    def test_unknown_industry_falls_back_to_generic_preset(self, api_client):
        # Use a valid industry choice but with no preset file to test the
        # fallback. All our industries have presets, so we fake via the
        # _load_preset path — skipping by using an empty preset check.
        from modules.dashboards.seed import _preset_path

        # Confirm generic.yaml exists as the fallback.
        assert _preset_path("nonexistent_industry").name == "generic.yaml"


@pytest.mark.django_db
class TestDashboardDataEndpoint:
    def test_data_returns_payload_per_widget(self, api_client):
        from modules.dashboards.seed import seed_default_dashboard

        company = CompanyFactory(industry="generic")
        user = UserFactory(company=company)
        seed_default_dashboard(company)
        dashboard = Dashboard.objects.get(company=company)
        auth(api_client, user)

        response = api_client.get(
            f"/api/v1/dashboards/dashboards/{dashboard.id}/data/"
        )
        assert response.status_code == 200
        body = response.json()
        # Response keyed by widget id; one entry per widget.
        widget_ids = list(
            DashboardWidget.objects.filter(dashboard=dashboard).values_list(
                "id", flat=True
            )
        )
        for wid in widget_ids:
            assert str(wid) in body or wid in body


@pytest.mark.django_db
class TestCompanyIsolation:
    def test_other_tenants_dashboard_hidden(self, api_client):
        from modules.dashboards.seed import seed_default_dashboard

        company_a = CompanyFactory(industry="generic")
        company_b = CompanyFactory(industry="generic")
        user_a = UserFactory(company=company_a)
        seed_default_dashboard(company_a)
        seed_default_dashboard(company_b)
        auth(api_client, user_a)

        response = api_client.get("/api/v1/dashboards/dashboards/")
        assert response.status_code == 200
        # Only company A's dashboard is visible.
        body = response.json()
        assert len(body) == 1
