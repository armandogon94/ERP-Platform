"""Model tests for the Point of Sale module (Slice 14)."""

from decimal import Decimal

import pytest

from core.factories import CompanyFactory, PartnerFactory, UserFactory
from modules.inventory.factories import ProductFactory
from modules.pos.factories import (
    CashMovementFactory,
    POSOrderFactory,
    POSOrderLineFactory,
    POSSessionFactory,
)
from modules.pos.models import CashMovement, POSOrder, POSOrderLine, POSSession


@pytest.mark.django_db
class TestPOSSession:
    def test_create_session(self):
        s = POSSessionFactory()
        assert s.pk is not None
        assert s.status == POSSession.Status.OPEN
        assert s.cash_on_open >= Decimal("0.00")

    def test_str_shows_station(self):
        s = POSSessionFactory(station="Bar-1")
        assert "Bar-1" in str(s)

    def test_company_isolation(self):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        POSSessionFactory(company=a)
        POSSessionFactory(company=b)
        assert POSSession.objects.filter(company=a).count() == 1


@pytest.mark.django_db
class TestPOSOrder:
    def test_create_order(self):
        o = POSOrderFactory()
        assert o.pk is not None
        assert o.status == POSOrder.Status.DRAFT

    def test_auto_order_number(self):
        o = POSOrderFactory(order_number="")
        assert o.order_number.startswith("POS/")

    def test_preset_order_number_preserved(self):
        o = POSOrderFactory(order_number="MANUAL-1")
        assert o.order_number == "MANUAL-1"

    def test_customer_nullable(self):
        o = POSOrderFactory(customer=None)
        assert o.customer is None

    def test_customer_fk_works(self):
        company = CompanyFactory()
        partner = PartnerFactory(company=company, is_customer=True)
        o = POSOrderFactory(company=company, customer=partner)
        assert o.customer_id == partner.id


@pytest.mark.django_db
class TestPOSOrderLine:
    def test_create_line(self):
        line = POSOrderLineFactory()
        assert line.pk is not None
        assert line.quantity > 0

    def test_total_stored(self):
        line = POSOrderLineFactory(
            quantity=Decimal("2.00"),
            unit_price=Decimal("9.99"),
            total=Decimal("19.98"),
        )
        assert line.total == Decimal("19.98")


@pytest.mark.django_db
class TestCashMovement:
    def test_create_in_movement(self):
        m = CashMovementFactory(type="in", amount=Decimal("50.00"))
        assert m.type == "in"
        assert m.amount == Decimal("50.00")

    def test_create_out_movement(self):
        m = CashMovementFactory(type="out", amount=Decimal("25.00"))
        assert m.type == "out"
