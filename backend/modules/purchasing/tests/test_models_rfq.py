"""Tests for Purchasing module RFQ models: RequestForQuote, RFQLine."""
import pytest
from decimal import Decimal

from core.factories import CompanyFactory
from modules.purchasing.factories import (
    RFQFactory,
    RFQLineFactory,
    VendorFactory,
)
from modules.purchasing.models import RequestForQuote, RFQLine


@pytest.mark.django_db
class TestRequestForQuoteModel:
    def test_create_rfq(self):
        company = CompanyFactory()
        vendor = VendorFactory(company=company)
        rfq = RequestForQuote.objects.create(
            company=company,
            vendor=vendor,
            rfq_number="RFQ-2026-001",
            status=RequestForQuote.Status.DRAFT,
        )
        assert rfq.pk is not None
        assert rfq.rfq_number == "RFQ-2026-001"
        assert rfq.vendor == vendor

    def test_rfq_str_contains_rfq_number(self):
        rfq = RFQFactory(rfq_number="RFQ-2026-042")
        assert "RFQ-2026-042" in str(rfq)

    def test_rfq_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        RFQFactory(company=c1)
        RFQFactory(company=c2)
        assert RequestForQuote.objects.filter(company=c1).count() == 1
        assert RequestForQuote.objects.filter(company=c2).count() == 1

    def test_rfq_status_choices(self):
        rfq = RFQFactory(status=RequestForQuote.Status.SENT)
        assert rfq.status == RequestForQuote.Status.SENT

    def test_rfq_factory(self):
        rfq = RFQFactory()
        assert rfq.pk is not None
        assert rfq.vendor is not None

    def test_rfq_soft_delete(self):
        rfq = RFQFactory()
        rfq.soft_delete()
        assert RequestForQuote.objects.filter(pk=rfq.pk).count() == 0
        assert RequestForQuote.all_objects.filter(pk=rfq.pk).count() == 1

    def test_rfq_default_status_is_draft(self):
        rfq = RFQFactory()
        assert rfq.status == RequestForQuote.Status.DRAFT


@pytest.mark.django_db
class TestRFQLineModel:
    def test_create_rfq_line(self):
        company = CompanyFactory()
        rfq = RFQFactory(company=company)
        line = RFQLine.objects.create(
            company=company,
            rfq=rfq,
            description="Dental mirrors x50",
            quantity=Decimal("50"),
            unit_price=Decimal("3.00"),
        )
        assert line.pk is not None
        assert line.quantity == Decimal("50")

    def test_rfq_line_str_contains_description(self):
        line = RFQLineFactory(description="Exam gloves box")
        assert "Exam gloves box" in str(line)

    def test_rfq_line_factory(self):
        line = RFQLineFactory()
        assert line.pk is not None
        assert line.rfq is not None

    def test_rfq_line_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        RFQLineFactory(company=c1)
        RFQLineFactory(company=c2)
        assert RFQLine.objects.filter(company=c1).count() == 1
        assert RFQLine.objects.filter(company=c2).count() == 1
