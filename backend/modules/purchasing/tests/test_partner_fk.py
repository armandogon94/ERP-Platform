"""Tests for Partner FK on PurchaseOrder (Slice 10.6).

PurchaseOrder keeps the legacy `vendor` FK to the per-module Vendor table
for backwards compatibility; the new `partner` FK points at core.Partner.
"""

import pytest

from core.factories import CompanyFactory, PartnerFactory
from modules.purchasing.factories import PurchaseOrderFactory, VendorFactory


@pytest.mark.django_db
class TestPurchaseOrderPartnerFK:
    def test_partner_fk_is_nullable(self):
        company = CompanyFactory()
        vendor = VendorFactory(company=company)
        po = PurchaseOrderFactory(company=company, vendor=vendor, partner=None)
        assert po.partner is None

    def test_assign_same_company_partner(self):
        company = CompanyFactory()
        vendor = VendorFactory(company=company)
        partner = PartnerFactory(company=company, name="Bulk Supplier", is_vendor=True)
        po = PurchaseOrderFactory(company=company, vendor=vendor, partner=partner)
        assert po.partner_id == partner.id
