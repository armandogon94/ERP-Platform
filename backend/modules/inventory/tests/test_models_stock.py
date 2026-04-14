"""Tests for StockLot, StockMove, ReorderRule models."""
import pytest
from decimal import Decimal
from django.utils import timezone

from core.factories import CompanyFactory
from modules.inventory.factories import (
    ProductFactory,
    ReorderRuleFactory,
    StockLocationFactory,
    StockLotFactory,
    StockMoveFactory,
)
from modules.inventory.models import ReorderRule, StockLot, StockMove


@pytest.mark.django_db
class TestStockLotModel:
    def test_create_lot(self):
        company = CompanyFactory()
        product = ProductFactory(company=company)
        lot = StockLot.objects.create(
            company=company,
            product=product,
            lot_number="LOT-001",
            quantity=Decimal("50"),
        )
        assert lot.pk is not None
        assert lot.lot_number == "LOT-001"

    def test_lot_str_contains_lot_number(self):
        lot = StockLotFactory(lot_number="BATCH-2026")
        assert "BATCH-2026" in str(lot)

    def test_lot_unique_per_product(self):
        company = CompanyFactory()
        product = ProductFactory(company=company)
        StockLotFactory(company=company, product=product, lot_number="LOT-1")
        with pytest.raises(Exception):
            StockLotFactory(company=company, product=product, lot_number="LOT-1")

    def test_lot_factory(self):
        lot = StockLotFactory()
        assert lot.pk is not None
        assert lot.product is not None

    def test_lot_expiry_date_nullable(self):
        lot = StockLotFactory(expiry_date=None)
        assert lot.expiry_date is None


@pytest.mark.django_db
class TestStockMoveModel:
    def test_create_stock_move(self):
        company = CompanyFactory()
        product = ProductFactory(company=company)
        src = StockLocationFactory(company=company, name="Warehouse")
        dst = StockLocationFactory(company=company, name="Customer")
        move = StockMove.objects.create(
            company=company,
            product=product,
            source_location=src,
            destination_location=dst,
            quantity=Decimal("10"),
            move_type=StockMove.MoveType.DELIVERY,
        )
        assert move.pk is not None
        assert move.quantity == Decimal("10")

    def test_stock_move_str_contains_product(self):
        move = StockMoveFactory()
        assert move.product.name in str(move)

    def test_stock_move_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        StockMoveFactory(company=c1)
        StockMoveFactory(company=c2)
        assert StockMove.objects.filter(company=c1).count() == 1

    def test_stock_move_status_choices(self):
        move = StockMoveFactory(status=StockMove.Status.CONFIRMED)
        assert move.status == StockMove.Status.CONFIRMED

    def test_stock_move_type_receipt(self):
        move = StockMoveFactory(move_type=StockMove.MoveType.RECEIPT)
        assert move.move_type == StockMove.MoveType.RECEIPT

    def test_stock_move_factory(self):
        move = StockMoveFactory()
        assert move.pk is not None
        assert move.source_location is not None
        assert move.destination_location is not None


@pytest.mark.django_db
class TestReorderRuleModel:
    def test_create_reorder_rule(self):
        company = CompanyFactory()
        product = ProductFactory(company=company)
        location = StockLocationFactory(company=company)
        rule = ReorderRule.objects.create(
            company=company,
            product=product,
            location=location,
            min_quantity=Decimal("5"),
            max_quantity=Decimal("100"),
            reorder_quantity=Decimal("50"),
        )
        assert rule.pk is not None
        assert rule.min_quantity == Decimal("5")

    def test_reorder_rule_str_contains_product(self):
        rule = ReorderRuleFactory()
        assert rule.product.name in str(rule)

    def test_reorder_rule_unique_per_product_location(self):
        company = CompanyFactory()
        product = ProductFactory(company=company)
        location = StockLocationFactory(company=company)
        ReorderRuleFactory(company=company, product=product, location=location)
        with pytest.raises(Exception):
            ReorderRuleFactory(company=company, product=product, location=location)

    def test_reorder_rule_factory(self):
        rule = ReorderRuleFactory()
        assert rule.pk is not None
        assert rule.product is not None
        assert rule.location is not None

    def test_reorder_rule_active_default(self):
        rule = ReorderRuleFactory()
        assert rule.is_active is True
