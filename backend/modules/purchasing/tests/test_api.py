"""Tests for Purchasing API endpoints."""
import pytest
from decimal import Decimal
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.purchasing.factories import (
    POLineFactory,
    PurchaseOrderFactory,
    RFQFactory,
    VendorFactory,
)
from modules.purchasing.models import PurchaseOrder, RequestForQuote


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


# ─── Vendors ─────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestVendorAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/purchasing/vendors/")
        assert response.status_code == 401

    def test_list_returns_company_vendors(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        VendorFactory(company=company, name="Acme Supplies")
        VendorFactory(company=company, name="MedLine")
        auth(api_client, user)

        response = api_client.get("/api/v1/purchasing/vendors/")
        assert response.status_code == 200
        names = [v["name"] for v in response.json()]
        assert "Acme Supplies" in names
        assert "MedLine" in names

    def test_vendors_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        VendorFactory(company=c1, name="C1 Vendor")
        VendorFactory(company=c2, name="C2 Vendor")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/purchasing/vendors/")
        names = [v["name"] for v in response.json()]
        assert "C1 Vendor" in names
        assert "C2 Vendor" not in names

    def test_create_vendor(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/purchasing/vendors/",
            {"name": "New Vendor", "email": "vendor@example.com"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "New Vendor"

    def test_retrieve_vendor(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        vendor = VendorFactory(company=company, name="Test Vendor")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/purchasing/vendors/{vendor.pk}/")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Vendor"

    def test_update_vendor(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        vendor = VendorFactory(company=company, name="Old Name")
        auth(api_client, user)

        response = api_client.patch(
            f"/api/v1/purchasing/vendors/{vendor.pk}/",
            {"name": "New Name"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    def test_filter_by_is_active(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        VendorFactory(company=company, name="Active Vendor", is_active=True)
        VendorFactory(company=company, name="Inactive Vendor", is_active=False)
        auth(api_client, user)

        response = api_client.get("/api/v1/purchasing/vendors/?is_active=true")
        names = [v["name"] for v in response.json()]
        assert "Active Vendor" in names
        assert "Inactive Vendor" not in names


# ─── Purchase Orders ──────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestPurchaseOrderAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/purchasing/purchase-orders/")
        assert response.status_code == 401

    def test_list_returns_company_pos(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        PurchaseOrderFactory(company=company, po_number="PO-001")
        PurchaseOrderFactory(company=company, po_number="PO-002")
        auth(api_client, user)

        response = api_client.get("/api/v1/purchasing/purchase-orders/")
        assert response.status_code == 200
        numbers = [p["po_number"] for p in response.json()]
        assert "PO-001" in numbers
        assert "PO-002" in numbers

    def test_pos_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        PurchaseOrderFactory(company=c1, po_number="C1-PO")
        PurchaseOrderFactory(company=c2, po_number="C2-PO")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/purchasing/purchase-orders/")
        numbers = [p["po_number"] for p in response.json()]
        assert "C1-PO" in numbers
        assert "C2-PO" not in numbers

    def test_create_purchase_order(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        vendor = VendorFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/purchasing/purchase-orders/",
            {
                "vendor": vendor.pk,
                "po_number": "PO-NEW-001",
                "status": PurchaseOrder.Status.DRAFT,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["po_number"] == "PO-NEW-001"

    def test_filter_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        PurchaseOrderFactory(company=company, po_number="DRAFT-PO", status=PurchaseOrder.Status.DRAFT)
        PurchaseOrderFactory(company=company, po_number="CONF-PO", status=PurchaseOrder.Status.CONFIRMED)
        auth(api_client, user)

        response = api_client.get("/api/v1/purchasing/purchase-orders/?status=draft")
        numbers = [p["po_number"] for p in response.json()]
        assert "DRAFT-PO" in numbers
        assert "CONF-PO" not in numbers


# ─── RFQs ────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestRFQAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/purchasing/rfqs/")
        assert response.status_code == 401

    def test_list_returns_company_rfqs(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        RFQFactory(company=company, rfq_number="RFQ-001")
        RFQFactory(company=company, rfq_number="RFQ-002")
        auth(api_client, user)

        response = api_client.get("/api/v1/purchasing/rfqs/")
        assert response.status_code == 200
        numbers = [r["rfq_number"] for r in response.json()]
        assert "RFQ-001" in numbers
        assert "RFQ-002" in numbers

    def test_rfqs_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        RFQFactory(company=c1, rfq_number="C1-RFQ")
        RFQFactory(company=c2, rfq_number="C2-RFQ")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/purchasing/rfqs/")
        numbers = [r["rfq_number"] for r in response.json()]
        assert "C1-RFQ" in numbers
        assert "C2-RFQ" not in numbers

    def test_create_rfq(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        vendor = VendorFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/purchasing/rfqs/",
            {
                "vendor": vendor.pk,
                "rfq_number": "RFQ-NEW-001",
                "status": RequestForQuote.Status.DRAFT,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["rfq_number"] == "RFQ-NEW-001"
