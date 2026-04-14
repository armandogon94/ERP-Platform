"""Tests for Invoicing API endpoints."""
import pytest
from decimal import Decimal
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.invoicing.factories import (
    CreditNoteFactory,
    InvoiceFactory,
    InvoiceLineFactory,
)
from modules.invoicing.models import Invoice


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


# ─── Invoices ─────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestInvoiceAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/invoicing/invoices/")
        assert response.status_code == 401

    def test_list_returns_company_invoices(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        InvoiceFactory(company=company, invoice_number="INV-001")
        InvoiceFactory(company=company, invoice_number="INV-002")
        auth(api_client, user)

        response = api_client.get("/api/v1/invoicing/invoices/")
        assert response.status_code == 200
        numbers = [i["invoice_number"] for i in response.json()]
        assert "INV-001" in numbers
        assert "INV-002" in numbers

    def test_invoices_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        InvoiceFactory(company=c1, invoice_number="C1-INV")
        InvoiceFactory(company=c2, invoice_number="C2-INV")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/invoicing/invoices/")
        numbers = [i["invoice_number"] for i in response.json()]
        assert "C1-INV" in numbers
        assert "C2-INV" not in numbers

    def test_create_invoice(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/invoicing/invoices/",
            {
                "invoice_number": "INV-NEW-001",
                "invoice_type": Invoice.InvoiceType.CUSTOMER,
                "customer_name": "Acme Corp",
                "status": Invoice.Status.DRAFT,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["invoice_number"] == "INV-NEW-001"

    def test_retrieve_invoice(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        inv = InvoiceFactory(company=company, invoice_number="INV-FETCH")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/invoicing/invoices/{inv.pk}/")
        assert response.status_code == 200
        assert response.json()["invoice_number"] == "INV-FETCH"

    def test_filter_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        InvoiceFactory(company=company, invoice_number="DRAFT-INV", status=Invoice.Status.DRAFT)
        InvoiceFactory(company=company, invoice_number="PAID-INV", status=Invoice.Status.PAID)
        auth(api_client, user)

        response = api_client.get("/api/v1/invoicing/invoices/?status=draft")
        numbers = [i["invoice_number"] for i in response.json()]
        assert "DRAFT-INV" in numbers
        assert "PAID-INV" not in numbers

    def test_filter_by_invoice_type(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        InvoiceFactory(company=company, invoice_number="CUST-INV", invoice_type=Invoice.InvoiceType.CUSTOMER)
        InvoiceFactory(company=company, invoice_number="VEND-INV", invoice_type=Invoice.InvoiceType.VENDOR)
        auth(api_client, user)

        response = api_client.get("/api/v1/invoicing/invoices/?invoice_type=customer")
        numbers = [i["invoice_number"] for i in response.json()]
        assert "CUST-INV" in numbers
        assert "VEND-INV" not in numbers

    def test_update_invoice(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        inv = InvoiceFactory(company=company, status=Invoice.Status.DRAFT)
        auth(api_client, user)

        response = api_client.patch(
            f"/api/v1/invoicing/invoices/{inv.pk}/",
            {"status": Invoice.Status.POSTED},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == Invoice.Status.POSTED


# ─── Credit Notes ─────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCreditNoteAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/invoicing/credit-notes/")
        assert response.status_code == 401

    def test_list_returns_company_credit_notes(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        CreditNoteFactory(company=company, credit_note_number="CN-001")
        CreditNoteFactory(company=company, credit_note_number="CN-002")
        auth(api_client, user)

        response = api_client.get("/api/v1/invoicing/credit-notes/")
        assert response.status_code == 200
        numbers = [cn["credit_note_number"] for cn in response.json()]
        assert "CN-001" in numbers
        assert "CN-002" in numbers

    def test_credit_notes_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        CreditNoteFactory(company=c1, credit_note_number="C1-CN")
        CreditNoteFactory(company=c2, credit_note_number="C2-CN")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/invoicing/credit-notes/")
        numbers = [cn["credit_note_number"] for cn in response.json()]
        assert "C1-CN" in numbers
        assert "C2-CN" not in numbers

    def test_create_credit_note(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        inv = InvoiceFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/invoicing/credit-notes/",
            {
                "credit_note_number": "CN-NEW-001",
                "invoice": inv.pk,
                "reason": "Product returned",
                "amount": "150.00",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["credit_note_number"] == "CN-NEW-001"
