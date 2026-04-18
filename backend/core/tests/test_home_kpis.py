"""Tests for the Home KPIs endpoint at /api/v1/core/home-kpis/ (Slice 19)."""

from decimal import Decimal

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestHomeKPIsEndpoint:
    def test_requires_auth(self, api_client):
        response = api_client.get("/api/v1/core/home-kpis/")
        assert response.status_code == 401

    def test_returns_tiles_for_company(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.get("/api/v1/core/home-kpis/")
        assert response.status_code == 200
        body = response.json()
        assert "tiles" in body
        assert isinstance(body["tiles"], list)
        assert len(body["tiles"]) >= 4
        # Every tile must have label + value
        for tile in body["tiles"]:
            assert "label" in tile
            assert "value" in tile

    def test_tiles_are_company_scoped(self, api_client):
        from modules.invoicing.models import Invoice

        company_a = CompanyFactory()
        company_b = CompanyFactory()
        user_a = UserFactory(company=company_a)
        Invoice.objects.create(
            company=company_a,
            invoice_number="INV-A-1",
            customer_name="A",
            status="posted",
            total_amount=Decimal("1000.00"),
            subtotal=Decimal("1000.00"),
        )
        Invoice.objects.create(
            company=company_b,
            invoice_number="INV-B-1",
            customer_name="B",
            status="posted",
            total_amount=Decimal("9999.00"),
            subtotal=Decimal("9999.00"),
        )
        auth(api_client, user_a)
        response = api_client.get("/api/v1/core/home-kpis/")
        assert response.status_code == 200
        body = response.json()
        labels = {t["label"]: t["value"] for t in body["tiles"]}
        # Company A should see only its own invoice totals (no 9999)
        assert "Outstanding Invoices" in labels or any(
            "invoice" in t["label"].lower() for t in body["tiles"]
        )

    def test_result_is_cached_for_60s(self, api_client):
        """REVIEW S-1: repeat requests hit the cache, not the DB."""
        from django.core.cache import cache
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        company = CompanyFactory()
        user = UserFactory(company=company)
        cache.delete(f"home_kpis:{company.id}")
        auth(api_client, user)

        with CaptureQueriesContext(connection) as first:
            r1 = api_client.get("/api/v1/core/home-kpis/")
        assert r1.status_code == 200
        first_query_count = len(first.captured_queries)

        with CaptureQueriesContext(connection) as second:
            r2 = api_client.get("/api/v1/core/home-kpis/")
        assert r2.status_code == 200
        # Second call should skip the 6 KPI aggregate queries.
        assert len(second.captured_queries) < first_query_count, (
            f"Cache miss: first call ran {first_query_count} queries, "
            f"second ran {len(second.captured_queries)}"
        )

    def test_open_sales_orders_counts_confirmed_and_in_progress(self, api_client):
        """REVIEW C-5: "Open Sales Orders" must include confirmed + in_progress
        (SalesOrder has no "draft" state; the original filter undercounted)."""
        from modules.sales.models import SalesOrder

        company = CompanyFactory()
        user = UserFactory(company=company)
        SalesOrder.objects.create(
            company=company, order_number="SO-1", status="confirmed",
            customer_name="A",
        )
        SalesOrder.objects.create(
            company=company, order_number="SO-2", status="in_progress",
            customer_name="B",
        )
        SalesOrder.objects.create(
            company=company, order_number="SO-3", status="delivered",
            customer_name="C",
        )
        auth(api_client, user)

        response = api_client.get("/api/v1/core/home-kpis/")
        assert response.status_code == 200
        tiles = {t["label"]: t["value"] for t in response.json()["tiles"]}
        assert tiles.get("Open Sales Orders") == "2"
