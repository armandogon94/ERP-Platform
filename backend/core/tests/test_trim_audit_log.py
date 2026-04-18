"""Tests for the trim_audit_log management command (REVIEW C-6)."""

from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from core.factories import CompanyFactory
from core.models import AuditLog


@pytest.mark.django_db
class TestTrimAuditLog:
    def test_deletes_rows_older_than_horizon(self):
        company = CompanyFactory()
        old_cutoff = timezone.now() - timedelta(days=100)
        recent = timezone.now() - timedelta(days=30)
        # Create then backdate — auto_now_add prevents setting at create time
        old = AuditLog.objects.create(
            company=company, model_name="Partner", model_id=1,
            action="create", new_values={},
        )
        AuditLog.objects.filter(pk=old.pk).update(timestamp=old_cutoff)
        new = AuditLog.objects.create(
            company=company, model_name="Partner", model_id=2,
            action="create", new_values={},
        )
        AuditLog.objects.filter(pk=new.pk).update(timestamp=recent)

        out = StringIO()
        call_command("trim_audit_log", "--days", "90", stdout=out)

        surviving = set(AuditLog.objects.values_list("pk", flat=True))
        assert old.pk not in surviving
        assert new.pk in surviving
        assert "Trimmed" in out.getvalue()

    def test_dry_run_does_not_delete(self):
        company = CompanyFactory()
        old = AuditLog.objects.create(
            company=company, model_name="Partner", model_id=1,
            action="create", new_values={},
        )
        AuditLog.objects.filter(pk=old.pk).update(
            timestamp=timezone.now() - timedelta(days=200),
        )

        out = StringIO()
        call_command("trim_audit_log", "--days", "30", "--dry-run", stdout=out)

        assert AuditLog.objects.filter(pk=old.pk).exists()
        assert "DRY RUN" in out.getvalue()

    def test_rejects_days_less_than_one(self):
        from django.core.management.base import CommandError

        with pytest.raises(CommandError):
            call_command("trim_audit_log", "--days", "0")
