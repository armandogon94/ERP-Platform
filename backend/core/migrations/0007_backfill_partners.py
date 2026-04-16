"""Back-fill Partner rows from existing `customer_name` strings and Vendor rows.

Creates one Partner per distinct `(company, name)` tuple across SalesQuotation,
SalesOrder, and Invoice (flagged `is_customer=True`), and one Partner per
Vendor (flagged `is_vendor=True`). Links the new FKs on existing rows.

Reverse migration clears the FK references but leaves Partner records in place.
This keeps the migration safe to roll back and re-apply without data loss.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    Partner = apps.get_model("core", "Partner")
    SalesQuotation = apps.get_model("sales", "SalesQuotation")
    SalesOrder = apps.get_model("sales", "SalesOrder")
    Invoice = apps.get_model("invoicing", "Invoice")
    Vendor = apps.get_model("purchasing", "Vendor")
    PurchaseOrder = apps.get_model("purchasing", "PurchaseOrder")

    # Customer-side: SalesQuotation + SalesOrder + Invoice → Partner(is_customer)
    for model in (SalesQuotation, SalesOrder, Invoice):
        qs = model.objects.filter(customer__isnull=True).exclude(customer_name="")
        for row in qs.iterator():
            partner, _ = Partner.objects.get_or_create(
                company_id=row.company_id,
                name=row.customer_name,
                tax_id="",
                defaults={"is_customer": True, "deleted_at": None},
            )
            if not partner.is_customer:
                partner.is_customer = True
                partner.save(update_fields=["is_customer"])
            row.customer_id = partner.id
            row.save(update_fields=["customer_id"])

    # Vendor-side: purchasing.Vendor → Partner(is_vendor); link PurchaseOrder.partner
    for vendor in Vendor.objects.all().iterator():
        partner, _ = Partner.objects.get_or_create(
            company_id=vendor.company_id,
            name=vendor.name,
            tax_id="",
            defaults={"is_vendor": True, "deleted_at": None},
        )
        if not partner.is_vendor:
            partner.is_vendor = True
            partner.save(update_fields=["is_vendor"])

        PurchaseOrder.objects.filter(
            company_id=vendor.company_id,
            vendor_id=vendor.id,
            partner__isnull=True,
        ).update(partner_id=partner.id)


def backwards(apps, schema_editor):
    SalesQuotation = apps.get_model("sales", "SalesQuotation")
    SalesOrder = apps.get_model("sales", "SalesOrder")
    Invoice = apps.get_model("invoicing", "Invoice")
    PurchaseOrder = apps.get_model("purchasing", "PurchaseOrder")
    SalesQuotation.objects.exclude(customer__isnull=True).update(customer=None)
    SalesOrder.objects.exclude(customer__isnull=True).update(customer=None)
    Invoice.objects.exclude(customer__isnull=True).update(customer=None)
    PurchaseOrder.objects.exclude(partner__isnull=True).update(partner=None)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_partner"),
        ("sales", "0002_salesorder_customer_salesquotation_customer"),
        ("invoicing", "0002_invoice_customer"),
        ("purchasing", "0003_purchaseorder_partner"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
