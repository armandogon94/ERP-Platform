import pytest

from core.factories import CompanyFactory, PartnerFactory, UserFactory
from core.models import AuditLog


@pytest.mark.django_db
class TestAuditLogSignals:
    """Audit pipeline uses Partner as the exemplar business model.

    REVIEW I-7 put framework-plumbing models (ModuleRegistry, Notification,
    Sequence, IndustryConfigTemplate, ViewDefinition) on an exclusion list
    to keep the audit timeline focused on user actions. Business models
    like Partner/Invoice/Ticket still audit normally.
    """

    def test_create_logs_audit_entry(self):
        company = CompanyFactory()
        partner = PartnerFactory(company=company, name="Acme")

        log = AuditLog.objects.filter(
            model_name="Partner",
            model_id=str(partner.pk),
            action="create",
        ).first()

        assert log is not None
        assert log.company == company
        assert log.new_values is not None

    def test_update_logs_audit_entry(self):
        company = CompanyFactory()
        partner = PartnerFactory(company=company, name="Acme")
        partner.name = "Acme Renamed"
        partner.save()

        logs = AuditLog.objects.filter(
            model_name="Partner",
            model_id=str(partner.pk),
            action="update",
        )
        assert logs.exists()

    def test_soft_delete_logs_audit_entry(self):
        company = CompanyFactory()
        partner = PartnerFactory(company=company, name="Acme")
        partner.soft_delete()

        logs = AuditLog.objects.filter(
            model_name="Partner",
            model_id=str(partner.pk),
            action="update",
        )
        # soft_delete is just an update (sets deleted_at)
        assert logs.exists()

    def test_audit_log_records_company(self):
        company = CompanyFactory()
        PartnerFactory(company=company, name="Acme")

        log = AuditLog.objects.filter(model_name="Partner").first()
        assert log.company == company

    def test_framework_models_are_excluded_from_audit(self):
        """REVIEW I-7: ModuleRegistry/Notification/Sequence do not pollute
        the user-facing audit timeline."""
        from core.models import ModuleRegistry, Notification
        company = CompanyFactory()
        user = UserFactory(company=company)
        ModuleRegistry.objects.create(
            company=company, name="hr", display_name="HR",
        )
        Notification.objects.create(
            recipient=user, title="hi", notification_type="info"
        )
        assert not AuditLog.objects.filter(
            model_name__in=["ModuleRegistry", "Notification"]
        ).exists()
