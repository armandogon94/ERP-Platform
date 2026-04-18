"""Trim AuditLog rows older than a retention horizon.

REVIEW C-6: without a retention policy, AuditLog grows unbounded
(every TenantModel save → 1 row). This command is designed to run
nightly (via Celery Beat, cron, or manual invocation):

    python manage.py trim_audit_log --days 90

It deletes any row whose ``timestamp`` is older than ``now - days``.
The default horizon is **90 days**, matching SOC 2 short-term retention
practice. Use ``--dry-run`` to preview without deleting.
"""

from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.models import AuditLog


class Command(BaseCommand):
    help = (
        "Delete AuditLog rows older than --days (default 90). "
        "Run nightly to bound table growth."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Retention horizon in days (default: 90)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report how many rows would be deleted but don't delete.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        if days < 1:
            raise CommandError("--days must be >= 1")

        cutoff = timezone.now() - timedelta(days=days)
        qs = AuditLog.objects.filter(timestamp__lt=cutoff)
        count = qs.count()

        if options["dry_run"]:
            self.stdout.write(
                f"DRY RUN — would delete {count} AuditLog rows older than {cutoff.isoformat()}"
            )
            return

        deleted, _detail = qs.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Trimmed {deleted} AuditLog rows older than {cutoff.isoformat()}"
            )
        )
