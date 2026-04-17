"""Sequence auto-generation for SalesQuotation + SalesOrder (Slice 10.7)."""

import pytest

from core.factories import CompanyFactory
from modules.sales.factories import SalesOrderFactory, SalesQuotationFactory


@pytest.mark.django_db
class TestSalesQuotationSequenceAutogen:
    def test_blank_number_is_auto_generated(self):
        company = CompanyFactory()
        q = SalesQuotationFactory(company=company, quotation_number="")
        assert q.quotation_number.startswith("QUO/")
        assert q.quotation_number.endswith("/00001")

    def test_preset_number_is_preserved(self):
        company = CompanyFactory()
        q = SalesQuotationFactory(company=company, quotation_number="MANUAL-Q-1")
        assert q.quotation_number == "MANUAL-Q-1"

    def test_second_quotation_increments(self):
        company = CompanyFactory()
        first = SalesQuotationFactory(company=company, quotation_number="")
        second = SalesQuotationFactory(company=company, quotation_number="")
        assert first.quotation_number.endswith("/00001")
        assert second.quotation_number.endswith("/00002")


@pytest.mark.django_db
class TestSalesOrderSequenceAutogen:
    def test_blank_number_is_auto_generated(self):
        company = CompanyFactory()
        so = SalesOrderFactory(company=company, order_number="")
        assert so.order_number.startswith("SO/")
        assert so.order_number.endswith("/00001")

    def test_preset_number_is_preserved(self):
        company = CompanyFactory()
        so = SalesOrderFactory(company=company, order_number="MANUAL-SO-1")
        assert so.order_number == "MANUAL-SO-1"
