from decimal import Decimal

import factory

from core.factories import CompanyFactory, UserFactory
from modules.inventory.factories import ProductFactory
from modules.pos.models import CashMovement, POSOrder, POSOrderLine, POSSession


class POSSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = POSSession
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    station = factory.Sequence(lambda n: f"Station-{n}")
    cash_on_open = Decimal("100.00")
    opened_by = factory.SubFactory(
        UserFactory, company=factory.SelfAttribute("..company")
    )
    status = POSSession.Status.OPEN


class POSOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = POSOrder
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    session = factory.SubFactory(
        POSSessionFactory, company=factory.SelfAttribute("..company")
    )
    customer = None
    subtotal = Decimal("0.00")
    tax_amount = Decimal("0.00")
    total = Decimal("0.00")
    status = POSOrder.Status.DRAFT


class POSOrderLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = POSOrderLine
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    order = factory.SubFactory(
        POSOrderFactory, company=factory.SelfAttribute("..company")
    )
    product = factory.SubFactory(
        ProductFactory, company=factory.SelfAttribute("..company")
    )
    quantity = Decimal("1.00")
    unit_price = Decimal("10.00")
    tax_rate = Decimal("0.00")
    total = Decimal("10.00")


class CashMovementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CashMovement
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    session = factory.SubFactory(
        POSSessionFactory, company=factory.SelfAttribute("..company")
    )
    type = CashMovement.MovementType.IN
    amount = Decimal("50.00")
    reason = "Pay-in"
