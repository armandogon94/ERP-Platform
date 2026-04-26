"""Tests for CompanyWebhookConfig (Slice 22).

The config holds per-company webhook peer URL + shared secret + status
fields. Spec: docs/CALENDAR-SYNC-WEBHOOKS.md §Configuration.
"""

import pytest

from core.factories import CompanyFactory


@pytest.mark.django_db
class TestCompanyWebhookConfig:
    def test_model_exists_and_has_all_fields(self):
        from core.models import CompanyWebhookConfig

        company = CompanyFactory()
        cfg = CompanyWebhookConfig.objects.create(
            company=company,
            peer_url="https://crm.example.com/api/v1/webhooks/calendar/novapay/",
            shared_secret="a" * 64,
            enabled=True,
        )
        assert cfg.pk is not None
        assert cfg.company == company
        assert cfg.enabled is True
        # Optional status fields default empty/null
        assert cfg.last_success_at is None
        assert cfg.last_error_at is None
        assert cfg.last_error_message == ""

    def test_enabled_defaults_false(self):
        from core.models import CompanyWebhookConfig

        company = CompanyFactory()
        cfg = CompanyWebhookConfig.objects.create(
            company=company,
            peer_url="https://example.com/hook/",
            shared_secret="secret",
        )
        assert cfg.enabled is False

    def test_one_to_one_with_company(self):
        """One config per company — second create should raise IntegrityError."""
        from django.db import IntegrityError

        from core.models import CompanyWebhookConfig

        company = CompanyFactory()
        CompanyWebhookConfig.objects.create(
            company=company,
            peer_url="https://example.com/hook/",
            shared_secret="secret",
        )
        with pytest.raises(IntegrityError):
            CompanyWebhookConfig.objects.create(
                company=company,
                peer_url="https://other.example.com/hook/",
                shared_secret="other",
            )

    def test_str_representation(self):
        from core.models import CompanyWebhookConfig

        company = CompanyFactory(slug="novapay")
        cfg = CompanyWebhookConfig.objects.create(
            company=company,
            peer_url="https://example.com/hook/",
            shared_secret="secret",
            enabled=True,
        )
        assert "novapay" in str(cfg)
