"""Tests for Invoicing module models: Invoice, InvoiceLine, CreditNote."""
import pytest
from decimal import Decimal

from core.factories import CompanyFactory
from modules.invoicing.factories import (
    CreditNoteFactory,
    InvoiceFactory,
    InvoiceLineFactory,
)
from modules.invoicing.models import CreditNote, Invoice, InvoiceLine


@pytest.mark.django_db
class TestInvoiceModel:
    def test_create_invoice(self):
        company = CompanyFactory()
        inv = Invoice.objects.create(
            company=company,
            invoice_number="INV-2026-001",
            invoice_type=Invoice.InvoiceType.CUSTOMER,
            status=Invoice.Status.DRAFT,
        )
        assert inv.pk is not None
        assert inv.invoice_number == "INV-2026-001"

    def test_invoice_str_contains_number(self):
        inv = InvoiceFactory(invoice_number="INV-2026-042")
        assert "INV-2026-042" in str(inv)

    def test_invoice_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        InvoiceFactory(company=c1)
        InvoiceFactory(company=c2)
        assert Invoice.objects.filter(company=c1).count() == 1
        assert Invoice.objects.filter(company=c2).count() == 1

    def test_invoice_type_choices(self):
        inv = InvoiceFactory(invoice_type=Invoice.InvoiceType.VENDOR)
        assert inv.invoice_type == Invoice.InvoiceType.VENDOR

    def test_invoice_status_choices(self):
        inv = InvoiceFactory(status=Invoice.Status.POSTED)
        assert inv.status == Invoice.Status.POSTED

    def test_invoice_factory(self):
        inv = InvoiceFactory()
        assert inv.pk is not None

    def test_invoice_soft_delete(self):
        inv = InvoiceFactory()
        inv.soft_delete()
        assert Invoice.objects.filter(pk=inv.pk).count() == 0
        assert Invoice.all_objects.filter(pk=inv.pk).count() == 1

    def test_invoice_default_status_is_draft(self):
        inv = InvoiceFactory()
        assert inv.status == Invoice.Status.DRAFT

    def test_invoice_default_type_is_customer(self):
        inv = InvoiceFactory()
        assert inv.invoice_type == Invoice.InvoiceType.CUSTOMER


@pytest.mark.django_db
class TestInvoiceLineModel:
    def test_create_invoice_line(self):
        company = CompanyFactory()
        inv = InvoiceFactory(company=company)
        line = InvoiceLine.objects.create(
            company=company,
            invoice=inv,
            description="Consulting services",
            quantity=Decimal("10"),
            unit_price=Decimal("150.00"),
        )
        assert line.pk is not None
        assert line.quantity == Decimal("10")

    def test_invoice_line_total_price(self):
        company = CompanyFactory()
        inv = InvoiceFactory(company=company)
        line = InvoiceLine.objects.create(
            company=company,
            invoice=inv,
            description="Software license",
            quantity=Decimal("1"),
            unit_price=Decimal("500.00"),
            total_price=Decimal("500.00"),
        )
        assert line.total_price == Decimal("500.00")

    def test_invoice_line_str_contains_description(self):
        line = InvoiceLineFactory(description="Annual maintenance fee")
        assert "Annual maintenance fee" in str(line)

    def test_invoice_line_factory(self):
        line = InvoiceLineFactory()
        assert line.pk is not None
        assert line.invoice is not None

    def test_invoice_line_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        InvoiceLineFactory(company=c1)
        InvoiceLineFactory(company=c2)
        assert InvoiceLine.objects.filter(company=c1).count() == 1
        assert InvoiceLine.objects.filter(company=c2).count() == 1


@pytest.mark.django_db
class TestCreditNoteModel:
    def test_create_credit_note(self):
        company = CompanyFactory()
        inv = InvoiceFactory(company=company)
        cn = CreditNote.objects.create(
            company=company,
            credit_note_number="CN-2026-001",
            invoice=inv,
            reason="Returned goods",
            amount=Decimal("250.00"),
        )
        assert cn.pk is not None
        assert cn.credit_note_number == "CN-2026-001"

    def test_credit_note_str_contains_number(self):
        cn = CreditNoteFactory(credit_note_number="CN-2026-007")
        assert "CN-2026-007" in str(cn)

    def test_credit_note_factory(self):
        cn = CreditNoteFactory()
        assert cn.pk is not None
        assert cn.invoice is not None

    def test_credit_note_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        CreditNoteFactory(company=c1)
        CreditNoteFactory(company=c2)
        assert CreditNote.objects.filter(company=c1).count() == 1
        assert CreditNote.objects.filter(company=c2).count() == 1

    def test_credit_note_soft_delete(self):
        cn = CreditNoteFactory()
        cn.soft_delete()
        assert CreditNote.objects.filter(pk=cn.pk).count() == 0
        assert CreditNote.all_objects.filter(pk=cn.pk).count() == 1
