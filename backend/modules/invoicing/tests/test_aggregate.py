"""Tests for the /aggregate/ action on InvoiceViewSet (Slice 16, D23)."""

from decimal import Decimal

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.invoicing.factories import InvoiceFactory


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestInvoiceAggregate:
    def test_aggregate_sum_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        InvoiceFactory(
            company=company,
            status="draft",
            total_amount=Decimal("100.00"),
            customer_name="A",
        )
        InvoiceFactory(
            company=company,
            status="draft",
            total_amount=Decimal("50.00"),
            customer_name="B",
        )
        InvoiceFactory(
            company=company,
            status="paid",
            total_amount=Decimal("200.00"),
            customer_name="C",
        )
        auth(api_client, user)

        response = api_client.get(
            "/api/v1/invoicing/invoices/aggregate/"
            "?group_by=status&measure=total_amount&op=sum"
        )
        assert response.status_code == 200, response.content
        rows = response.json()
        by_group = {r["group"]: r["value"] for r in rows}
        assert by_group == {"draft": 150.0, "paid": 200.0}

    def test_aggregate_count_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        InvoiceFactory(company=company, status="draft", customer_name="A")
        InvoiceFactory(company=company, status="draft", customer_name="B")
        InvoiceFactory(company=company, status="paid", customer_name="C")
        auth(api_client, user)

        response = api_client.get(
            "/api/v1/invoicing/invoices/aggregate/?group_by=status&op=count"
        )
        rows = response.json()
        by_group = {r["group"]: r["value"] for r in rows}
        assert by_group == {"draft": 2, "paid": 1}

    def test_aggregate_rejects_non_whitelisted_group_by(self, api_client):
        """Security — group_by must be in the whitelist."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.get(
            "/api/v1/invoicing/invoices/aggregate/?group_by=deleted_at&op=count"
        )
        assert response.status_code == 400
        assert "not aggregatable" in response.json()["detail"]

    def test_aggregate_rejects_non_whitelisted_measure(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.get(
            "/api/v1/invoicing/invoices/aggregate/"
            "?group_by=status&measure=deleted_at&op=sum"
        )
        assert response.status_code == 400

    def test_aggregate_rejects_unknown_op(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.get(
            "/api/v1/invoicing/invoices/aggregate/"
            "?group_by=status&measure=total_amount&op=rce"
        )
        assert response.status_code == 400

    def test_aggregate_scoped_to_company(self, api_client):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        user = UserFactory(company=a)
        InvoiceFactory(company=a, status="paid", total_amount=Decimal("100.00"))
        InvoiceFactory(company=b, status="paid", total_amount=Decimal("999.00"))
        auth(api_client, user)
        response = api_client.get(
            "/api/v1/invoicing/invoices/aggregate/"
            "?group_by=status&measure=total_amount&op=sum"
        )
        rows = response.json()
        by_group = {r["group"]: r["value"] for r in rows}
        assert by_group == {"paid": 100.0}
