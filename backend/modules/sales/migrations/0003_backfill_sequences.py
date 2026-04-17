"""Back-fill blank quotation_number / order_number (Slice 10.7)."""

from django.db import migrations


def forwards(apps, schema_editor):
    from modules.sales.models import SalesOrder, SalesQuotation

    for row in SalesQuotation.objects.filter(quotation_number="").order_by("created_at"):
        row.save(update_fields=None)

    for row in SalesOrder.objects.filter(order_number="").order_by("created_at"):
        row.save(update_fields=None)


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0002_salesorder_customer_salesquotation_customer"),
        ("core", "0007_backfill_partners"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
