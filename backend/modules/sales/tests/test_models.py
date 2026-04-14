"""Tests for Sales module models: SalesQuotation, SalesOrder, SalesOrderLine."""
import pytest
from decimal import Decimal

from core.factories import CompanyFactory
from modules.sales.factories import (
    SalesOrderFactory,
    SalesOrderLineFactory,
    SalesQuotationFactory,
)
from modules.sales.models import SalesOrder, SalesOrderLine, SalesQuotation


@pytest.mark.django_db
class TestSalesQuotationModel:
    def test_create_quotation(self):
        company = CompanyFactory()
        q = SalesQuotation.objects.create(
            company=company,
            quotation_number="QUO-2026-001",
            status=SalesQuotation.Status.DRAFT,
        )
        assert q.pk is not None
        assert q.quotation_number == "QUO-2026-001"

    def test_quotation_str_contains_number(self):
        q = SalesQuotationFactory(quotation_number="QUO-2026-042")
        assert "QUO-2026-042" in str(q)

    def test_quotation_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        SalesQuotationFactory(company=c1)
        SalesQuotationFactory(company=c2)
        assert SalesQuotation.objects.filter(company=c1).count() == 1
        assert SalesQuotation.objects.filter(company=c2).count() == 1

    def test_quotation_status_choices(self):
        q = SalesQuotationFactory(status=SalesQuotation.Status.SENT)
        assert q.status == SalesQuotation.Status.SENT

    def test_quotation_factory(self):
        q = SalesQuotationFactory()
        assert q.pk is not None

    def test_quotation_soft_delete(self):
        q = SalesQuotationFactory()
        q.soft_delete()
        assert SalesQuotation.objects.filter(pk=q.pk).count() == 0
        assert SalesQuotation.all_objects.filter(pk=q.pk).count() == 1

    def test_quotation_default_status_is_draft(self):
        q = SalesQuotationFactory()
        assert q.status == SalesQuotation.Status.DRAFT


@pytest.mark.django_db
class TestSalesOrderModel:
    def test_create_sales_order(self):
        company = CompanyFactory()
        so = SalesOrder.objects.create(
            company=company,
            order_number="SO-2026-001",
            status=SalesOrder.Status.CONFIRMED,
        )
        assert so.pk is not None
        assert so.order_number == "SO-2026-001"

    def test_sales_order_str_contains_number(self):
        so = SalesOrderFactory(order_number="SO-2026-042")
        assert "SO-2026-042" in str(so)

    def test_sales_order_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        SalesOrderFactory(company=c1)
        SalesOrderFactory(company=c2)
        assert SalesOrder.objects.filter(company=c1).count() == 1
        assert SalesOrder.objects.filter(company=c2).count() == 1

    def test_sales_order_status_choices(self):
        so = SalesOrderFactory(status=SalesOrder.Status.DELIVERED)
        assert so.status == SalesOrder.Status.DELIVERED

    def test_sales_order_factory(self):
        so = SalesOrderFactory()
        assert so.pk is not None

    def test_sales_order_soft_delete(self):
        so = SalesOrderFactory()
        so.soft_delete()
        assert SalesOrder.objects.filter(pk=so.pk).count() == 0
        assert SalesOrder.all_objects.filter(pk=so.pk).count() == 1

    def test_sales_order_default_status_is_confirmed(self):
        so = SalesOrderFactory()
        assert so.status == SalesOrder.Status.CONFIRMED


@pytest.mark.django_db
class TestSalesOrderLineModel:
    def test_create_line(self):
        company = CompanyFactory()
        so = SalesOrderFactory(company=company)
        line = SalesOrderLine.objects.create(
            company=company,
            sales_order=so,
            description="Widget x10",
            quantity=Decimal("10"),
            unit_price=Decimal("5.00"),
        )
        assert line.pk is not None
        assert line.quantity == Decimal("10")

    def test_line_total_price(self):
        company = CompanyFactory()
        so = SalesOrderFactory(company=company)
        line = SalesOrderLine.objects.create(
            company=company,
            sales_order=so,
            description="Gadget",
            quantity=Decimal("4"),
            unit_price=Decimal("25.00"),
            total_price=Decimal("100.00"),
        )
        assert line.total_price == Decimal("100.00")

    def test_line_str_contains_description(self):
        line = SalesOrderLineFactory(description="Premium widget")
        assert "Premium widget" in str(line)

    def test_line_factory(self):
        line = SalesOrderLineFactory()
        assert line.pk is not None
        assert line.sales_order is not None

    def test_line_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        SalesOrderLineFactory(company=c1)
        SalesOrderLineFactory(company=c2)
        assert SalesOrderLine.objects.filter(company=c1).count() == 1
        assert SalesOrderLine.objects.filter(company=c2).count() == 1
