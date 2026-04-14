"""Tests for Sales API endpoints."""
import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.sales.factories import (
    SalesOrderFactory,
    SalesOrderLineFactory,
    SalesQuotationFactory,
)
from modules.sales.models import SalesOrder, SalesQuotation


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


# ─── Quotations ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSalesQuotationAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/sales/quotations/")
        assert response.status_code == 401

    def test_list_returns_company_quotations(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        SalesQuotationFactory(company=company, quotation_number="QUO-001")
        SalesQuotationFactory(company=company, quotation_number="QUO-002")
        auth(api_client, user)

        response = api_client.get("/api/v1/sales/quotations/")
        assert response.status_code == 200
        numbers = [q["quotation_number"] for q in response.json()]
        assert "QUO-001" in numbers
        assert "QUO-002" in numbers

    def test_quotations_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        SalesQuotationFactory(company=c1, quotation_number="C1-QUO")
        SalesQuotationFactory(company=c2, quotation_number="C2-QUO")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/sales/quotations/")
        numbers = [q["quotation_number"] for q in response.json()]
        assert "C1-QUO" in numbers
        assert "C2-QUO" not in numbers

    def test_create_quotation(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/sales/quotations/",
            {
                "quotation_number": "QUO-NEW-001",
                "customer_name": "Acme Corp",
                "status": SalesQuotation.Status.DRAFT,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["quotation_number"] == "QUO-NEW-001"

    def test_retrieve_quotation(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        q = SalesQuotationFactory(company=company, quotation_number="QUO-999")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/sales/quotations/{q.pk}/")
        assert response.status_code == 200
        assert response.json()["quotation_number"] == "QUO-999"

    def test_filter_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        SalesQuotationFactory(company=company, quotation_number="DRAFT-QUO", status=SalesQuotation.Status.DRAFT)
        SalesQuotationFactory(company=company, quotation_number="SENT-QUO", status=SalesQuotation.Status.SENT)
        auth(api_client, user)

        response = api_client.get("/api/v1/sales/quotations/?status=draft")
        numbers = [q["quotation_number"] for q in response.json()]
        assert "DRAFT-QUO" in numbers
        assert "SENT-QUO" not in numbers


# ─── Sales Orders ─────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSalesOrderAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/sales/orders/")
        assert response.status_code == 401

    def test_list_returns_company_orders(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        SalesOrderFactory(company=company, order_number="SO-001")
        SalesOrderFactory(company=company, order_number="SO-002")
        auth(api_client, user)

        response = api_client.get("/api/v1/sales/orders/")
        assert response.status_code == 200
        numbers = [o["order_number"] for o in response.json()]
        assert "SO-001" in numbers
        assert "SO-002" in numbers

    def test_orders_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        SalesOrderFactory(company=c1, order_number="C1-SO")
        SalesOrderFactory(company=c2, order_number="C2-SO")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/sales/orders/")
        numbers = [o["order_number"] for o in response.json()]
        assert "C1-SO" in numbers
        assert "C2-SO" not in numbers

    def test_create_sales_order(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/sales/orders/",
            {
                "order_number": "SO-NEW-001",
                "customer_name": "Acme Corp",
                "status": SalesOrder.Status.CONFIRMED,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["order_number"] == "SO-NEW-001"

    def test_filter_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        SalesOrderFactory(company=company, order_number="CONF-SO", status=SalesOrder.Status.CONFIRMED)
        SalesOrderFactory(company=company, order_number="DELIV-SO", status=SalesOrder.Status.DELIVERED)
        auth(api_client, user)

        response = api_client.get("/api/v1/sales/orders/?status=confirmed")
        numbers = [o["order_number"] for o in response.json()]
        assert "CONF-SO" in numbers
        assert "DELIV-SO" not in numbers

    def test_update_sales_order(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        so = SalesOrderFactory(company=company, order_number="SO-OLD")
        auth(api_client, user)

        response = api_client.patch(
            f"/api/v1/sales/orders/{so.pk}/",
            {"order_number": "SO-UPDATED"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["order_number"] == "SO-UPDATED"
