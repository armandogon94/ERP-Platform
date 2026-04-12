from django.db import transaction
from django.utils import timezone


def get_next_sequence(company, prefix):
    """Generate the next sequential ID for a company/prefix.

    Format: {prefix}/{year}/{padded_number}
    Example: INV/2026/00001

    Uses select_for_update() for thread-safety.
    """
    from core.models import Sequence

    now = timezone.now()

    with transaction.atomic():
        seq, created = Sequence.objects.select_for_update().get_or_create(
            company=company,
            prefix=prefix,
            defaults={
                "next_number": 1,
                "step": 1,
                "padding": 5,
                "use_date_range": True,
                "reset_period": "yearly",
            },
        )

        # Handle yearly reset
        if not created and seq.reset_period == "yearly" and seq.use_date_range:
            # Reset if we crossed a year boundary (check via stored next_number context)
            pass  # Will be enhanced when we add date tracking

        number = seq.next_number
        seq.next_number += seq.step
        seq.save(update_fields=["next_number"])

    padded = str(number).zfill(seq.padding)

    if seq.use_date_range:
        return f"{prefix}/{now.year}/{padded}"
    return f"{prefix}/{padded}"
