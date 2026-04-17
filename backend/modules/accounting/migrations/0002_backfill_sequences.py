"""Back-fill blank JournalEntry.reference (Slice 10.7)."""

from django.db import migrations


def forwards(apps, schema_editor):
    from modules.accounting.models import JournalEntry

    for row in JournalEntry.objects.filter(reference="").order_by("created_at"):
        row.save(update_fields=None)


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("accounting", "0001_initial"),
        ("core", "0007_backfill_partners"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
