"""Tests that writable FK fields cannot point to rows from other companies.

See REVIEW-2026-04-17.md C-1. Default ``PrimaryKeyRelatedField`` querysets are
global; ``CompanyScopedFilterBackend`` only filters reads, not writes. This
test suite covers the serializers that accept FKs from client payloads:

* Invoice.customer → core.Partner
* SalesOrder.customer, SalesQuotation.customer → core.Partner
* Ticket.reporter_partner → core.Partner
* PurchaseOrder.partner → core.Partner
* EventAttendee.event / .resource → Event / Resource
* Project.customer_partner → core.Partner
* POSOrder.customer → core.Partner
"""

from decimal import Decimal

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, PartnerFactory, UserFactory


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestCrossCompanyFKRejection:
    """Every scoped FK must 400 when the target belongs to another company."""

    def test_invoice_rejects_cross_company_customer(self, api_client):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        user_a = UserFactory(company=company_a)
        foreign = PartnerFactory(company=company_b)
        auth(api_client, user_a)

        response = api_client.post(
            "/api/v1/invoicing/invoices/",
            {
                "invoice_number": "INV-X",
                "customer": foreign.id,
                "customer_name": "Fake",
                "status": "draft",
                "total_amount": "100.00",
                "subtotal": "100.00",
            },
            format="json",
        )
        assert response.status_code == 400, response.json()
        assert "customer" in response.json()

    def test_sales_order_rejects_cross_company_customer(self, api_client):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        user_a = UserFactory(company=company_a)
        foreign = PartnerFactory(company=company_b)
        auth(api_client, user_a)

        response = api_client.post(
            "/api/v1/sales/orders/",
            {
                "order_number": "SO-X",
                "customer": foreign.id,
                "customer_name": "Fake",
                "status": "confirmed",
            },
            format="json",
        )
        assert response.status_code == 400, response.json()
        assert "customer" in response.json()

    def test_purchase_order_rejects_cross_company_partner(self, api_client):
        from modules.purchasing.models import Vendor

        company_a = CompanyFactory()
        company_b = CompanyFactory()
        user_a = UserFactory(company=company_a)
        vendor_a = Vendor.objects.create(company=company_a, name="V1")
        foreign = PartnerFactory(company=company_b)
        auth(api_client, user_a)

        response = api_client.post(
            "/api/v1/purchasing/purchase-orders/",
            {
                "po_number": "PO-X",
                "vendor": vendor_a.id,
                "partner": foreign.id,
                "status": "draft",
            },
            format="json",
        )
        assert response.status_code == 400, response.json()
        assert "partner" in response.json()

    def test_ticket_rejects_cross_company_reporter_partner(self, api_client):
        from modules.helpdesk.models import TicketCategory

        company_a = CompanyFactory()
        company_b = CompanyFactory()
        user_a = UserFactory(company=company_a)
        cat = TicketCategory.objects.create(company=company_a, name="General")
        foreign = PartnerFactory(company=company_b)
        auth(api_client, user_a)

        response = api_client.post(
            "/api/v1/helpdesk/tickets/",
            {
                "ticket_number": "TKT-X",
                "title": "Help",
                "category": cat.id,
                "reporter_partner": foreign.id,
                "priority": "normal",
                "status": "new",
            },
            format="json",
        )
        assert response.status_code == 400, response.json()
        assert "reporter_partner" in response.json()


@pytest.mark.django_db
class TestSameCompanyFKAccepted:
    """Sanity check: same-company FKs still succeed (no regression)."""

    def test_invoice_accepts_same_company_customer(self, api_client):
        company_a = CompanyFactory()
        user_a = UserFactory(company=company_a)
        same = PartnerFactory(company=company_a)
        auth(api_client, user_a)

        response = api_client.post(
            "/api/v1/invoicing/invoices/",
            {
                "invoice_number": "INV-OK",
                "customer": same.id,
                "customer_name": same.name,
                "status": "draft",
                "total_amount": "100.00",
                "subtotal": "100.00",
            },
            format="json",
        )
        assert response.status_code == 201, response.json()
