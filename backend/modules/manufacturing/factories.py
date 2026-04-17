from decimal import Decimal

import factory

from core.factories import CompanyFactory
from modules.inventory.factories import ProductFactory
from modules.manufacturing.models import (
    BillOfMaterials,
    BOMLine,
    ProductionCost,
    WorkOrder,
)


class BillOfMaterialsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BillOfMaterials
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    product = factory.SubFactory(
        ProductFactory, company=factory.SelfAttribute("..company")
    )
    version = "1.0"
    active = True


class BOMLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BOMLine
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    bom = factory.SubFactory(
        BillOfMaterialsFactory, company=factory.SelfAttribute("..company")
    )
    component = factory.SubFactory(
        ProductFactory, company=factory.SelfAttribute("..company")
    )
    quantity = Decimal("1.00")
    uom = "unit"


class WorkOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkOrder
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    product = factory.SubFactory(
        ProductFactory, company=factory.SelfAttribute("..company")
    )
    bom = None
    quantity_target = Decimal("10.00")
    quantity_done = Decimal("0.00")
    status = WorkOrder.Status.DRAFT


class ProductionCostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductionCost
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    work_order = factory.SubFactory(
        WorkOrderFactory, company=factory.SelfAttribute("..company")
    )
    cost_type = ProductionCost.CostType.MATERIAL
    amount = Decimal("50.00")
    notes = ""
