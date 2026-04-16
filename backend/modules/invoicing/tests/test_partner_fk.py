"""Tests for Partner FK on Invoice (Slice 10.6)."""

import pytest

from core.factories import CompanyFactory, PartnerFactory
from modules.invoicing.factories import InvoiceFactory


@pytest.mark.django_db
class TestInvoicePartnerFK:
    def test_customer_fk_is_nullable(self):
        company = CompanyFactory()
        inv = InvoiceFactory(company=company, customer=None)
        assert inv.customer is None

    def test_assign_same_company_partner(self):
        company = CompanyFactory()
        partner = PartnerFactory(company=company, name="Acme")
        inv = InvoiceFactory(company=company, customer=partner)
        assert inv.customer_id == partner.id
