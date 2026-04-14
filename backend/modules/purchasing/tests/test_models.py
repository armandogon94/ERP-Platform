"""Tests for Purchasing module models: Vendor, PurchaseOrder, POLine."""
import pytest
from decimal import Decimal

from core.factories import CompanyFactory
from modules.purchasing.factories import (
    POLineFactory,
    PurchaseOrderFactory,
    VendorFactory,
)
from modules.purchasing.models import POLine, PurchaseOrder, Vendor


@pytest.mark.django_db
class TestVendorModel:
    def test_create_vendor(self):
        company = CompanyFactory()
        vendor = Vendor.objects.create(
            company=company,
            name="Acme Dental Supplies",
            email="orders@acme.com",
        )
        assert vendor.pk is not None
        assert vendor.name == "Acme Dental Supplies"
        assert vendor.company == company

    def test_vendor_str_contains_name(self):
        vendor = VendorFactory(name="MedLine Industries")
        assert "MedLine Industries" in str(vendor)

    def test_vendor_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        VendorFactory(company=c1)
        VendorFactory(company=c2)
        assert Vendor.objects.filter(company=c1).count() == 1
        assert Vendor.objects.filter(company=c2).count() == 1

    def test_vendor_is_active_default(self):
        vendor = VendorFactory()
        assert vendor.is_active is True

    def test_vendor_factory(self):
        vendor = VendorFactory()
        assert vendor.pk is not None
        assert vendor.company is not None

    def test_vendor_soft_delete(self):
        vendor = VendorFactory()
        vendor.soft_delete()
        assert Vendor.objects.filter(pk=vendor.pk).count() == 0
        assert Vendor.all_objects.filter(pk=vendor.pk).count() == 1

    def test_vendor_payment_terms_choices(self):
        vendor = VendorFactory(payment_terms=Vendor.PaymentTerms.NET_60)
        assert vendor.payment_terms == Vendor.PaymentTerms.NET_60


@pytest.mark.django_db
class TestPurchaseOrderModel:
    def test_create_purchase_order(self):
        company = CompanyFactory()
        vendor = VendorFactory(company=company)
        po = PurchaseOrder.objects.create(
            company=company,
            vendor=vendor,
            po_number="PO-2026-001",
            status=PurchaseOrder.Status.DRAFT,
        )
        assert po.pk is not None
        assert po.po_number == "PO-2026-001"
        assert po.vendor == vendor

    def test_po_str_contains_po_number(self):
        po = PurchaseOrderFactory(po_number="PO-2026-042")
        assert "PO-2026-042" in str(po)

    def test_po_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        PurchaseOrderFactory(company=c1)
        PurchaseOrderFactory(company=c2)
        assert PurchaseOrder.objects.filter(company=c1).count() == 1
        assert PurchaseOrder.objects.filter(company=c2).count() == 1

    def test_po_status_choices(self):
        po = PurchaseOrderFactory(status=PurchaseOrder.Status.CONFIRMED)
        assert po.status == PurchaseOrder.Status.CONFIRMED

    def test_po_factory(self):
        po = PurchaseOrderFactory()
        assert po.pk is not None
        assert po.vendor is not None

    def test_po_soft_delete(self):
        po = PurchaseOrderFactory()
        po.soft_delete()
        assert PurchaseOrder.objects.filter(pk=po.pk).count() == 0
        assert PurchaseOrder.all_objects.filter(pk=po.pk).count() == 1


@pytest.mark.django_db
class TestPOLineModel:
    def test_create_po_line(self):
        company = CompanyFactory()
        po = PurchaseOrderFactory(company=company)
        line = POLine.objects.create(
            company=company,
            purchase_order=po,
            description="Dental mirrors x100",
            quantity=Decimal("100"),
            unit_price=Decimal("2.50"),
        )
        assert line.pk is not None
        assert line.quantity == Decimal("100")

    def test_po_line_total_price(self):
        company = CompanyFactory()
        po = PurchaseOrderFactory(company=company)
        line = POLine.objects.create(
            company=company,
            purchase_order=po,
            description="Gloves",
            quantity=Decimal("10"),
            unit_price=Decimal("5.00"),
            total_price=Decimal("50.00"),
        )
        assert line.total_price == Decimal("50.00")

    def test_po_line_str_contains_description(self):
        line = POLineFactory(description="Exam gloves")
        assert "Exam gloves" in str(line)

    def test_po_line_factory(self):
        line = POLineFactory()
        assert line.pk is not None
        assert line.purchase_order is not None

    def test_po_line_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        POLineFactory(company=c1)
        POLineFactory(company=c2)
        assert POLine.objects.filter(company=c1).count() == 1
