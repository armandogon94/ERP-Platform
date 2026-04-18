"""HTTP-layer tests for reports endpoints (REVIEW C-8).

Before this file, the Reports module had 482 LOC and only 50 LOC of tests —
model-only assertions with no `test_api.py`. The `/reports/templates/`,
`/reports/pivots/`, and `/reports/schedules/` endpoints were entirely
unexercised at the HTTP layer.
"""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.reports.models import PivotDefinition, ReportTemplate, ScheduledExport


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestReportTemplateAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/reports/templates/")
        assert response.status_code == 401

    def test_create_assigns_company_from_request(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/reports/templates/",
            {
                "name": "Monthly Sales",
                "model_name": "sales.SalesOrder",
                "default_group_by": ["customer_name"],
                "default_measures": ["total_amount"],
            },
            format="json",
        )
        assert response.status_code == 201, response.json()
        template = ReportTemplate.objects.get(pk=response.json()["id"])
        assert template.company == company

    def test_list_is_company_scoped(self, api_client):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        user_a = UserFactory(company=company_a)
        ReportTemplate.objects.create(
            company=company_a, name="A-Template", model_name="sales.SalesOrder"
        )
        ReportTemplate.objects.create(
            company=company_b, name="B-Template", model_name="sales.SalesOrder"
        )
        auth(api_client, user_a)
        response = api_client.get("/api/v1/reports/templates/")
        names = [t["name"] for t in response.json()]
        assert "A-Template" in names
        assert "B-Template" not in names


@pytest.mark.django_db
class TestPivotDefinitionAPI:
    def test_create_and_retrieve(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/reports/pivots/",
            {
                "name": "Invoices by Customer",
                "model_name": "invoicing.Invoice",
                "rows": ["customer_name"],
                "cols": ["status"],
                "measure": "total_amount",
                "aggregator": "sum",
            },
            format="json",
        )
        assert response.status_code == 201, response.json()
        pivot = PivotDefinition.objects.get(pk=response.json()["id"])
        assert pivot.rows == ["customer_name"]
        assert pivot.measure == "total_amount"

    def test_list_is_company_scoped(self, api_client):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        user_a = UserFactory(company=company_a)
        PivotDefinition.objects.create(
            company=company_a, name="A", model_name="sales.SalesOrder",
            rows=["customer_name"], measure="total_amount",
        )
        PivotDefinition.objects.create(
            company=company_b, name="B", model_name="sales.SalesOrder",
            rows=["customer_name"], measure="total_amount",
        )
        auth(api_client, user_a)
        response = api_client.get("/api/v1/reports/pivots/")
        names = [p["name"] for p in response.json()]
        assert "A" in names
        assert "B" not in names


@pytest.mark.django_db
class TestScheduledExportAPI:
    def test_create_requires_existing_template(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        template = ReportTemplate.objects.create(
            company=company, name="T", model_name="sales.SalesOrder",
        )
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/reports/schedules/",
            {
                "report": template.id,
                "cron": "0 8 * * 1",
                "format": "pdf",
                "recipients": ["ops@example.com"],
            },
            format="json",
        )
        assert response.status_code == 201, response.json()
        schedule = ScheduledExport.objects.get(pk=response.json()["id"])
        assert schedule.report == template

    def test_cannot_schedule_another_tenants_template(self, api_client):
        """REVIEW C-1 regression: cross-company FK writes must be rejected."""
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        user_a = UserFactory(company=company_a)
        foreign_template = ReportTemplate.objects.create(
            company=company_b, name="B-Template", model_name="sales.SalesOrder",
        )
        auth(api_client, user_a)
        response = api_client.post(
            "/api/v1/reports/schedules/",
            {
                "report": foreign_template.id,
                "cron": "0 8 * * 1",
                "format": "csv",
                "recipients": [],
            },
            format="json",
        )
        assert response.status_code == 400, response.json()


@pytest.mark.django_db
class TestAggregateEndpoint:
    """Aggregate endpoints live on each module's ViewSet, not reports/."""

    def test_aggregate_rejects_non_whitelisted_field(self, api_client):
        from modules.invoicing.models import Invoice

        company = CompanyFactory()
        user = UserFactory(company=company)
        Invoice.objects.create(
            company=company, invoice_number="INV-1", customer_name="A",
            status="posted", total_amount="100.00", subtotal="100.00",
        )
        auth(api_client, user)

        # Try an unwhitelisted groupBy field — must 400.
        response = api_client.get(
            "/api/v1/invoicing/invoices/aggregate/",
            {"groupBy": "subtotal", "measure": "id", "aggregator": "count"},
        )
        # subtotal is not in invoicing's aggregatable_fields whitelist
        assert response.status_code == 400, (
            f"Expected 400 for non-whitelisted field, got {response.status_code}"
        )
