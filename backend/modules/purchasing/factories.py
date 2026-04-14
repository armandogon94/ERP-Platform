import factory
from decimal import Decimal

from core.factories import CompanyFactory
from modules.purchasing.models import POLine, PurchaseOrder, RequestForQuote, RFQLine, Vendor


class VendorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vendor
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Vendor {n}")
    email = factory.Sequence(lambda n: f"vendor{n}@example.com")
    contact_name = ""
    phone = ""
    address = ""
    currency = "USD"
    payment_terms = Vendor.PaymentTerms.NET_30
    is_active = True


class PurchaseOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PurchaseOrder
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    vendor = factory.SubFactory(VendorFactory, company=factory.SelfAttribute("..company"))
    po_number = factory.Sequence(lambda n: f"PO-2026-{n:03d}")
    status = PurchaseOrder.Status.DRAFT
    total_amount = Decimal("0.00")


class RFQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RequestForQuote
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    vendor = factory.SubFactory(VendorFactory, company=factory.SelfAttribute("..company"))
    rfq_number = factory.Sequence(lambda n: f"RFQ-2026-{n:03d}")
    status = RequestForQuote.Status.DRAFT


class RFQLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RFQLine
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    rfq = factory.SubFactory(RFQFactory, company=factory.SelfAttribute("..company"))
    description = factory.Sequence(lambda n: f"RFQ line item {n}")
    quantity = Decimal("1.00")
    unit_price = Decimal("10.00")


class POLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = POLine
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    purchase_order = factory.SubFactory(
        PurchaseOrderFactory, company=factory.SelfAttribute("..company")
    )
    description = factory.Sequence(lambda n: f"Line item {n}")
    quantity = Decimal("1.00")
    unit_price = Decimal("10.00")
    total_price = Decimal("10.00")
