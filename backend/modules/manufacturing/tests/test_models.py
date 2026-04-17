"""Model tests for the Manufacturing module (Slice 13)."""

from decimal import Decimal

import pytest

from core.factories import CompanyFactory
from modules.inventory.factories import ProductFactory
from modules.manufacturing.factories import (
    BillOfMaterialsFactory,
    BOMLineFactory,
    ProductionCostFactory,
    WorkOrderFactory,
)
from modules.manufacturing.models import (
    BillOfMaterials,
    BOMLine,
    ProductionCost,
    WorkOrder,
)


@pytest.mark.django_db
class TestBillOfMaterials:
    def test_create_bom(self):
        bom = BillOfMaterialsFactory()
        assert bom.pk is not None
        assert bom.active is True
        assert bom.version == "1.0"

    def test_str_shows_product_version(self):
        company = CompanyFactory()
        product = ProductFactory(company=company, name="Widget")
        bom = BillOfMaterialsFactory(
            company=company, product=product, version="2.0"
        )
        s = str(bom)
        assert "Widget" in s
        assert "2.0" in s

    def test_company_isolation(self):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        BillOfMaterialsFactory(company=a)
        BillOfMaterialsFactory(company=b)
        assert BillOfMaterials.objects.filter(company=a).count() == 1


@pytest.mark.django_db
class TestBOMLine:
    def test_create_line(self):
        line = BOMLineFactory()
        assert line.pk is not None
        assert line.quantity > 0

    def test_component_fk(self):
        company = CompanyFactory()
        bom_product = ProductFactory(company=company, name="Finished")
        component = ProductFactory(company=company, name="Part")
        bom = BillOfMaterialsFactory(company=company, product=bom_product)
        line = BOMLineFactory(
            company=company, bom=bom, component=component, quantity=Decimal("3.00")
        )
        assert line.component_id == component.id
        assert line.quantity == Decimal("3.00")


@pytest.mark.django_db
class TestWorkOrder:
    def test_create_work_order(self):
        wo = WorkOrderFactory()
        assert wo.pk is not None
        assert wo.status == WorkOrder.Status.DRAFT
        assert wo.quantity_target > 0

    def test_str_shows_product(self):
        company = CompanyFactory()
        product = ProductFactory(company=company, name="Cake")
        wo = WorkOrderFactory(company=company, product=product)
        assert "Cake" in str(wo)


@pytest.mark.django_db
class TestProductionCost:
    def test_create_cost(self):
        cost = ProductionCostFactory()
        assert cost.pk is not None
        assert cost.cost_type == ProductionCost.CostType.MATERIAL

    def test_amount_decimal_precision(self):
        cost = ProductionCostFactory(amount=Decimal("125.75"))
        assert cost.amount == Decimal("125.75")
