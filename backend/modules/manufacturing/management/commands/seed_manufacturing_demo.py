from decimal import Decimal

from core.management.commands._seed_helpers import SeedCommandBase
from modules.inventory.models import Product
from modules.manufacturing.models import (
    BillOfMaterials,
    BOMLine,
    WorkOrder,
)


class Command(SeedCommandBase):
    help = "Seed a demo BOM + work order (requires a product). Idempotent."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            WorkOrder.objects.filter(company=company).delete()
            BOMLine.objects.filter(company=company).delete()
            BillOfMaterials.objects.filter(company=company).delete()

        product, _ = Product.objects.get_or_create(
            company=company,
            sku="DEMO-MFG-FINISHED",
            defaults={"name": "Demo Finished Good", "sale_price": Decimal("50.00")},
        )
        component, _ = Product.objects.get_or_create(
            company=company,
            sku="DEMO-MFG-PART",
            defaults={"name": "Demo Component", "cost_price": Decimal("5.00")},
        )
        bom, _ = BillOfMaterials.objects.get_or_create(
            company=company,
            product=product,
            version="1.0",
            defaults={"active": True},
        )
        BOMLine.objects.get_or_create(
            company=company,
            bom=bom,
            component=component,
            defaults={"quantity": Decimal("2.00"), "uom": "unit"},
        )
        WorkOrder.objects.get_or_create(
            company=company,
            product=product,
            bom=bom,
            status="confirmed",
            defaults={"quantity_target": Decimal("10.00")},
        )
        return 4
