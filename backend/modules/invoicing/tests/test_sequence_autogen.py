"""Sequence auto-generation for Invoice + CreditNote (Slice 10.7, D22)."""

import pytest

from core.factories import CompanyFactory
from modules.invoicing.factories import CreditNoteFactory, InvoiceFactory


@pytest.mark.django_db
class TestInvoiceSequenceAutogen:
    def test_blank_number_is_auto_generated(self):
        company = CompanyFactory()
        invoice = InvoiceFactory(company=company, invoice_number="")
        assert invoice.invoice_number.startswith("INV/")
        assert invoice.invoice_number.endswith("/00001")

    def test_preset_number_is_preserved(self):
        company = CompanyFactory()
        invoice = InvoiceFactory(company=company, invoice_number="MANUAL-42")
        assert invoice.invoice_number == "MANUAL-42"

    def test_second_invoice_increments(self):
        company = CompanyFactory()
        first = InvoiceFactory(company=company, invoice_number="")
        second = InvoiceFactory(company=company, invoice_number="")
        assert first.invoice_number.endswith("/00001")
        assert second.invoice_number.endswith("/00002")

    def test_different_companies_independent(self):
        company_a = CompanyFactory(slug="co-a")
        company_b = CompanyFactory(slug="co-b")
        a = InvoiceFactory(company=company_a, invoice_number="")
        b = InvoiceFactory(company=company_b, invoice_number="")
        assert a.invoice_number.endswith("/00001")
        assert b.invoice_number.endswith("/00001")


@pytest.mark.django_db
class TestCreditNoteSequenceAutogen:
    def test_blank_number_is_auto_generated(self):
        company = CompanyFactory()
        invoice = InvoiceFactory(company=company)
        cn = CreditNoteFactory(company=company, invoice=invoice, credit_note_number="")
        assert cn.credit_note_number.startswith("CN/")
        assert cn.credit_note_number.endswith("/00001")

    def test_preset_number_is_preserved(self):
        company = CompanyFactory()
        invoice = InvoiceFactory(company=company)
        cn = CreditNoteFactory(
            company=company, invoice=invoice, credit_note_number="CN-X-1"
        )
        assert cn.credit_note_number == "CN-X-1"
