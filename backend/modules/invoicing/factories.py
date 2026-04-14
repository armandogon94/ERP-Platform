import factory
from decimal import Decimal

from core.factories import CompanyFactory
from modules.invoicing.models import CreditNote, Invoice, InvoiceLine


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    invoice_number = factory.Sequence(lambda n: f"INV-2026-{n:03d}")
    invoice_type = Invoice.InvoiceType.CUSTOMER
    status = Invoice.Status.DRAFT
    customer_name = factory.Sequence(lambda n: f"Customer {n}")
    customer_email = factory.Sequence(lambda n: f"customer{n}@example.com")
    total_amount = Decimal("0.00")


class InvoiceLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceLine
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    invoice = factory.SubFactory(InvoiceFactory, company=factory.SelfAttribute("..company"))
    description = factory.Sequence(lambda n: f"Service line {n}")
    quantity = Decimal("1.00")
    unit_price = Decimal("100.00")
    tax_rate = Decimal("0.00")
    total_price = Decimal("100.00")


class CreditNoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CreditNote
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    credit_note_number = factory.Sequence(lambda n: f"CN-2026-{n:03d}")
    invoice = factory.SubFactory(InvoiceFactory, company=factory.SelfAttribute("..company"))
    reason = "Credit adjustment"
    amount = Decimal("50.00")
