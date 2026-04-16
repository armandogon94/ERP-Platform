"""Tests for Partner FK on SalesQuotation + SalesOrder (Slice 10.6)."""

import pytest

from core.factories import CompanyFactory, PartnerFactory
from modules.sales.factories import SalesOrderFactory, SalesQuotationFactory


@pytest.mark.django_db
class TestSalesQuotationPartnerFK:
    def test_customer_fk_is_nullable(self):
        company = CompanyFactory()
        q = SalesQuotationFactory(company=company, customer=None)
        assert q.customer is None

    def test_assign_same_company_partner(self):
        company = CompanyFactory()
        partner = PartnerFactory(company=company, name="Acme")
        q = SalesQuotationFactory(company=company, customer=partner)
        assert q.customer_id == partner.id


@pytest.mark.django_db
class TestSalesOrderPartnerFK:
    def test_customer_fk_is_nullable(self):
        company = CompanyFactory()
        so = SalesOrderFactory(company=company, customer=None)
        assert so.customer is None

    def test_assign_same_company_partner(self):
        company = CompanyFactory()
        partner = PartnerFactory(company=company, name="Globex")
        so = SalesOrderFactory(company=company, customer=partner)
        assert so.customer_id == partner.id
