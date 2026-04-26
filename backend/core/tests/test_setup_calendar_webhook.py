"""Tests for `python manage.py setup_calendar_webhook` (Slice 22)."""

from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from core.factories import CompanyFactory
from core.models import CompanyWebhookConfig


@pytest.mark.django_db
class TestSetupCalendarWebhook:
    def test_creates_config_for_company(self):
        company = CompanyFactory(slug="novapay")

        out = StringIO()
        call_command(
            "setup_calendar_webhook",
            "--company", "novapay",
            "--peer-url", "https://crm.example.com/api/v1/webhooks/calendar/novapay/",
            "--shared-secret", "0" * 64,
            stdout=out,
        )

        cfg = CompanyWebhookConfig.objects.get(company=company)
        assert cfg.peer_url.startswith("https://crm.example.com")
        assert cfg.shared_secret == "0" * 64
        assert cfg.enabled is False  # default until --enable
        assert "novapay" in out.getvalue()

    def test_idempotent_update(self):
        company = CompanyFactory(slug="novapay")
        CompanyWebhookConfig.objects.create(
            company=company,
            peer_url="https://old.example.com/",
            shared_secret="old",
            enabled=True,
        )

        call_command(
            "setup_calendar_webhook",
            "--company", "novapay",
            "--peer-url", "https://new.example.com/api/v1/webhooks/calendar/novapay/",
            "--shared-secret", "deadbeef",
        )

        cfg = CompanyWebhookConfig.objects.get(company=company)
        assert cfg.peer_url.startswith("https://new.example.com")
        assert cfg.shared_secret == "deadbeef"
        # `--enable`/`--disable` not passed → preserve existing flag.
        assert cfg.enabled is True
        # Still exactly one row.
        assert CompanyWebhookConfig.objects.filter(company=company).count() == 1

    def test_enable_flag(self):
        CompanyFactory(slug="novapay")
        call_command(
            "setup_calendar_webhook",
            "--company", "novapay",
            "--peer-url", "https://x.example.com/",
            "--shared-secret", "deadbeef",
            "--enable",
        )
        cfg = CompanyWebhookConfig.objects.get(company__slug="novapay")
        assert cfg.enabled is True

    def test_disable_flag(self):
        company = CompanyFactory(slug="novapay")
        CompanyWebhookConfig.objects.create(
            company=company,
            peer_url="https://x.example.com/",
            shared_secret="x",
            enabled=True,
        )
        call_command(
            "setup_calendar_webhook",
            "--company", "novapay",
            "--peer-url", "https://x.example.com/",
            "--shared-secret", "x",
            "--disable",
        )
        cfg = CompanyWebhookConfig.objects.get(company=company)
        assert cfg.enabled is False

    def test_unknown_company_errors(self):
        with pytest.raises(CommandError):
            call_command(
                "setup_calendar_webhook",
                "--company", "ghost",
                "--peer-url", "https://x.example.com/",
                "--shared-secret", "x",
            )

    def test_enable_and_disable_flags_conflict(self):
        CompanyFactory(slug="novapay")
        with pytest.raises(CommandError):
            call_command(
                "setup_calendar_webhook",
                "--company", "novapay",
                "--peer-url", "https://x.example.com/",
                "--shared-secret", "x",
                "--enable",
                "--disable",
            )
