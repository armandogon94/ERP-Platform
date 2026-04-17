from decimal import Decimal

from core.management.commands._seed_helpers import SeedCommandBase
from modules.inventory.models import Product, ProductCategory, StockLocation


class Command(SeedCommandBase):
    help = "Seed demo inventory (category + products + default location)."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            Product.objects.filter(company=company).delete()
            StockLocation.objects.filter(company=company).delete()
            ProductCategory.objects.filter(company=company).delete()

        category, _ = ProductCategory.objects.get_or_create(
            company=company, name="Demo Supplies"
        )
        StockLocation.objects.get_or_create(
            company=company,
            name="Main Warehouse",
            defaults={"location_type": "internal"},
        )
        seeds = [
            ("DEMO-SKU-1", "Sample Widget", Decimal("25.00"), Decimal("10.00")),
            ("DEMO-SKU-2", "Sample Service Plan", Decimal("50.00"), Decimal("20.00")),
            ("DEMO-SKU-3", "Sample Consumable", Decimal("5.00"), Decimal("2.00")),
        ]
        for sku, name, sale, cost in seeds:
            Product.objects.get_or_create(
                company=company,
                sku=sku,
                defaults={
                    "name": name,
                    "category": category,
                    "sale_price": sale,
                    "cost_price": cost,
                },
            )
        return len(seeds) + 2
