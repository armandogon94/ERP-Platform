import pytest

from core.factories import CompanyFactory, UserFactory
from core.models import AuditLog, ModuleRegistry


@pytest.mark.django_db
class TestAuditLogSignals:
    def test_create_logs_audit_entry(self):
        company = CompanyFactory()
        mod = ModuleRegistry.objects.create(
            company=company, name="hr", display_name="HR",
        )

        log = AuditLog.objects.filter(
            model_name="ModuleRegistry",
            model_id=str(mod.pk),
            action="create",
        ).first()

        assert log is not None
        assert log.company == company
        assert log.new_values is not None

    def test_update_logs_audit_entry(self):
        company = CompanyFactory()
        mod = ModuleRegistry.objects.create(
            company=company, name="hr", display_name="HR",
        )
        mod.display_name = "Human Resources"
        mod.save()

        logs = AuditLog.objects.filter(
            model_name="ModuleRegistry",
            model_id=str(mod.pk),
            action="update",
        )
        assert logs.exists()

    def test_soft_delete_logs_audit_entry(self):
        company = CompanyFactory()
        mod = ModuleRegistry.objects.create(
            company=company, name="hr", display_name="HR",
        )
        mod.soft_delete()

        logs = AuditLog.objects.filter(
            model_name="ModuleRegistry",
            model_id=str(mod.pk),
            action="update",
        )
        # soft_delete is just an update (sets deleted_at)
        assert logs.exists()

    def test_audit_log_records_company(self):
        company = CompanyFactory()
        ModuleRegistry.objects.create(
            company=company, name="inv", display_name="Inventory",
        )

        log = AuditLog.objects.filter(model_name="ModuleRegistry").first()
        assert log.company == company
