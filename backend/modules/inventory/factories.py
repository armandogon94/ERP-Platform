import factory
from decimal import Decimal
from django.utils import timezone

from core.factories import CompanyFactory
from modules.inventory.models import (
    Product,
    ProductCategory,
    ReorderRule,
    StockLocation,
    StockLot,
    StockMove,
)


class ProductCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductCategory
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Category {n}")
    description = ""
    parent = None


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Product {n}")
    sku = factory.Sequence(lambda n: f"SKU-{n:04d}")
    description = ""
    category = None
    unit_of_measure = Product.UOM.EACH
    cost_price = Decimal("10.00")
    sale_price = Decimal("15.00")
    reorder_point = Decimal("5.00")
    min_stock_level = Decimal("0.00")
    is_active = True


class StockLocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StockLocation
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Location {n}")
    location_type = StockLocation.LocationType.INTERNAL
    parent = None
    is_active = True


class StockLotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StockLot
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    product = factory.SubFactory(ProductFactory, company=factory.SelfAttribute("..company"))
    lot_number = factory.Sequence(lambda n: f"LOT-{n:04d}")
    expiry_date = factory.LazyFunction(
        lambda: (timezone.now() + timezone.timedelta(days=365)).date()
    )
    quantity = Decimal("100.00")


class StockMoveFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StockMove
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    product = factory.SubFactory(ProductFactory, company=factory.SelfAttribute("..company"))
    source_location = factory.SubFactory(
        StockLocationFactory, company=factory.SelfAttribute("..company")
    )
    destination_location = factory.SubFactory(
        StockLocationFactory, company=factory.SelfAttribute("..company")
    )
    quantity = Decimal("10.00")
    move_type = StockMove.MoveType.INTERNAL
    status = StockMove.Status.DRAFT
    reference = ""
    move_date = factory.LazyFunction(lambda: timezone.now().date())


class ReorderRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReorderRule
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    product = factory.SubFactory(ProductFactory, company=factory.SelfAttribute("..company"))
    location = factory.SubFactory(
        StockLocationFactory, company=factory.SelfAttribute("..company")
    )
    min_quantity = Decimal("5.00")
    max_quantity = Decimal("100.00")
    reorder_quantity = Decimal("50.00")
    is_active = True
