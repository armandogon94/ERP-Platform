"""API tests for the Point of Sale module (Slice 14)."""

from decimal import Decimal

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.inventory.factories import ProductFactory
from modules.pos.factories import (
    CashMovementFactory,
    POSOrderFactory,
    POSOrderLineFactory,
    POSSessionFactory,
)
from modules.pos.models import POSOrder, POSSession


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestPOSSessionAPI:
    def test_list_requires_auth(self, api_client):
        assert api_client.get("/api/v1/pos/sessions/").status_code == 401

    def test_list_scopes_to_company(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        POSSessionFactory(company=company, station="Mine")
        POSSessionFactory(station="Other")
        auth(api_client, user)
        response = api_client.get("/api/v1/pos/sessions/")
        assert response.status_code == 200
        stations = [s["station"] for s in response.json()]
        assert "Mine" in stations
        assert "Other" not in stations

    def test_create_session(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/pos/sessions/",
            {"station": "Bar-1", "cash_on_open": "150.00"},
            format="json",
        )
        assert response.status_code == 201, response.content
        assert response.json()["station"] == "Bar-1"

    def test_close_computes_variance(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        session = POSSessionFactory(
            company=company,
            station="S1",
            cash_on_open=Decimal("100.00"),
        )
        # +50 pay-in, -20 pay-out, +1 order total of 30
        CashMovementFactory(
            company=company, session=session, type="in", amount=Decimal("50.00")
        )
        CashMovementFactory(
            company=company, session=session, type="out", amount=Decimal("20.00")
        )
        POSOrderFactory(
            company=company,
            session=session,
            total=Decimal("30.00"),
            status=POSOrder.Status.PAID,
        )
        auth(api_client, user)

        response = api_client.post(
            f"/api/v1/pos/sessions/{session.pk}/close/",
            {"cash_on_close": "155.00"},
            format="json",
        )
        assert response.status_code == 200, response.content
        body = response.json()
        session.refresh_from_db()
        # expected = 100 + 50 - 20 + 30 = 160; actual 155; variance = 155-160 = -5
        assert Decimal(body["expected_cash"]) == Decimal("160.00")
        assert Decimal(body["variance"]) == Decimal("-5.00")
        assert session.status == "closed"

    def test_close_rejects_already_closed(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        session = POSSessionFactory(
            company=company,
            status=POSSession.Status.CLOSED,
        )
        auth(api_client, user)
        response = api_client.post(
            f"/api/v1/pos/sessions/{session.pk}/close/",
            {"cash_on_close": "100.00"},
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestPOSOrderAPI:
    def test_create_order_with_auto_number(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        session = POSSessionFactory(company=company)
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/pos/orders/",
            {"session": session.id, "total": "15.00", "status": "draft"},
            format="json",
        )
        assert response.status_code == 201, response.content
        assert response.json()["order_number"].startswith("POS/")

    def test_filter_by_session(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        s1 = POSSessionFactory(company=company)
        s2 = POSSessionFactory(company=company)
        POSOrderFactory(company=company, session=s1)
        POSOrderFactory(company=company, session=s2)
        auth(api_client, user)
        response = api_client.get(f"/api/v1/pos/orders/?session={s1.id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_filter_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        POSOrderFactory(company=company, status="paid")
        POSOrderFactory(company=company, status="draft")
        auth(api_client, user)
        response = api_client.get("/api/v1/pos/orders/?status=paid")
        statuses = [o["status"] for o in response.json()]
        assert statuses == ["paid"]


@pytest.mark.django_db
class TestPOSOrderLineAPI:
    def test_filter_by_order(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        o1 = POSOrderFactory(company=company)
        o2 = POSOrderFactory(company=company)
        POSOrderLineFactory(company=company, order=o1)
        POSOrderLineFactory(company=company, order=o2)
        auth(api_client, user)
        response = api_client.get(
            f"/api/v1/pos/order-lines/?order={o1.id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.django_db
class TestCashMovementAPI:
    def test_filter_by_session(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        s1 = POSSessionFactory(company=company)
        s2 = POSSessionFactory(company=company)
        CashMovementFactory(company=company, session=s1)
        CashMovementFactory(company=company, session=s2)
        auth(api_client, user)
        response = api_client.get(
            f"/api/v1/pos/cash-movements/?session={s1.id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
