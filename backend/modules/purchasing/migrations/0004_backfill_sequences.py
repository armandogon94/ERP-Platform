"""Back-fill blank po_number / rfq_number for existing rows (Slice 10.7)."""

from django.db import migrations


def forwards(apps, schema_editor):
    from modules.purchasing.models import PurchaseOrder, RequestForQuote

    for row in PurchaseOrder.objects.filter(po_number="").order_by("created_at"):
        row.save(update_fields=None)

    for row in RequestForQuote.objects.filter(rfq_number="").order_by("created_at"):
        row.save(update_fields=None)


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("purchasing", "0003_purchaseorder_partner"),
        ("core", "0007_backfill_partners"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
