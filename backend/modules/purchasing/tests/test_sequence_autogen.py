"""Sequence auto-generation for PurchaseOrder + RequestForQuote (Slice 10.7)."""

import pytest

from core.factories import CompanyFactory
from modules.purchasing.factories import PurchaseOrderFactory, RFQFactory


@pytest.mark.django_db
class TestPurchaseOrderSequenceAutogen:
    def test_blank_number_is_auto_generated(self):
        company = CompanyFactory()
        po = PurchaseOrderFactory(company=company, po_number="")
        assert po.po_number.startswith("PO/")
        assert po.po_number.endswith("/00001")

    def test_preset_number_is_preserved(self):
        company = CompanyFactory()
        po = PurchaseOrderFactory(company=company, po_number="MANUAL-PO-1")
        assert po.po_number == "MANUAL-PO-1"

    def test_second_po_increments(self):
        company = CompanyFactory()
        first = PurchaseOrderFactory(company=company, po_number="")
        second = PurchaseOrderFactory(company=company, po_number="")
        assert first.po_number.endswith("/00001")
        assert second.po_number.endswith("/00002")


@pytest.mark.django_db
class TestRFQSequenceAutogen:
    def test_blank_number_is_auto_generated(self):
        company = CompanyFactory()
        rfq = RFQFactory(company=company, rfq_number="")
        assert rfq.rfq_number.startswith("RFQ/")
        assert rfq.rfq_number.endswith("/00001")

    def test_preset_number_is_preserved(self):
        company = CompanyFactory()
        rfq = RFQFactory(company=company, rfq_number="MANUAL-RFQ-1")
        assert rfq.rfq_number == "MANUAL-RFQ-1"
