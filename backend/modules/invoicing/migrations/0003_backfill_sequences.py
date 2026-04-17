"""Back-fill blank invoice_number / credit_note_number for existing rows.

Assigns sequence numbers via the Invoice.save() / CreditNote.save() override
path (which calls core.sequence.get_next_sequence). Iterates in created_at
order so numbering is stable and reproducible.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    # NOTE: we use the live Invoice/CreditNote classes (not apps.get_model) so
    # the save() override fires and populates numbers via get_next_sequence.
    # This is safe because at this point in history, the save() logic is
    # already deployed (it's a forward migration in the same commit).
    from modules.invoicing.models import CreditNote, Invoice

    for row in Invoice.objects.filter(invoice_number="").order_by("created_at"):
        row.save(update_fields=None)  # triggers save() override → sets number

    for row in CreditNote.objects.filter(credit_note_number="").order_by("created_at"):
        row.save(update_fields=None)


def backwards(apps, schema_editor):
    # No-op: leaving the assigned numbers in place is safer than clearing them.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("invoicing", "0002_invoice_customer"),
        ("core", "0007_backfill_partners"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
