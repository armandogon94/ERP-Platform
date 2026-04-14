import factory
from decimal import Decimal

from core.factories import CompanyFactory
from modules.sales.models import SalesOrder, SalesOrderLine, SalesQuotation


class SalesQuotationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SalesQuotation
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    quotation_number = factory.Sequence(lambda n: f"QUO-2026-{n:03d}")
    customer_name = factory.Sequence(lambda n: f"Customer {n}")
    customer_email = factory.Sequence(lambda n: f"customer{n}@example.com")
    status = SalesQuotation.Status.DRAFT
    total_amount = Decimal("0.00")


class SalesOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SalesOrder
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    order_number = factory.Sequence(lambda n: f"SO-2026-{n:03d}")
    customer_name = factory.Sequence(lambda n: f"Customer {n}")
    customer_email = factory.Sequence(lambda n: f"customer{n}@example.com")
    quotation = None
    status = SalesOrder.Status.CONFIRMED
    total_amount = Decimal("0.00")


class SalesOrderLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SalesOrderLine
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    sales_order = factory.SubFactory(
        SalesOrderFactory, company=factory.SelfAttribute("..company")
    )
    description = factory.Sequence(lambda n: f"Line item {n}")
    quantity = Decimal("1.00")
    unit_price = Decimal("10.00")
    total_price = Decimal("10.00")
