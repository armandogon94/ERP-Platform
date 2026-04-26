"""Tests for the post_save signal that enqueues outbound webhooks.

Spec: docs/CALENDAR-SYNC-WEBHOOKS.md §Loop prevention.

The signal hook MUST:
1. Enqueue ``fire_calendar_webhook`` on every Event create/update.
2. Skip if ``instance._skip_webhook is True`` (loop guard set by the
   receiver before saving).
3. Skip if the company has no webhook config or it's disabled
   (don't waste broker queue time on no-ops).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.factories import CompanyFactory
from core.models import CompanyWebhookConfig
from modules.calendar.factories import EventFactory


def _setup_config(company, *, enabled: bool = True):
    return CompanyWebhookConfig.objects.create(
        company=company,
        peer_url="https://crm.example.com/api/v1/webhooks/calendar/x/",
        shared_secret="0" * 64,
        enabled=enabled,
    )


@pytest.mark.django_db
class TestWebhookSignal:
    def test_event_create_enqueues_webhook(self):
        company = CompanyFactory()
        _setup_config(company)
        with patch(
            "modules.calendar.signals.fire_calendar_webhook.delay"
        ) as mock_delay:
            event = EventFactory(company=company, external_uid="uid-sig")

        mock_delay.assert_called_once_with(event.pk, "event.upserted")

    def test_event_update_enqueues_webhook(self):
        company = CompanyFactory()
        _setup_config(company)
        event = EventFactory(company=company, external_uid="uid-upd")

        with patch(
            "modules.calendar.signals.fire_calendar_webhook.delay"
        ) as mock_delay:
            event.title = "renamed"
            event.save()

        mock_delay.assert_called_once_with(event.pk, "event.upserted")

    def test_skip_webhook_flag_short_circuits(self):
        """REVIEW LOOP-PREVENTION: receiver sets _skip_webhook=True."""
        company = CompanyFactory()
        _setup_config(company)
        event = EventFactory(company=company, external_uid="uid-loop")

        with patch(
            "modules.calendar.signals.fire_calendar_webhook.delay"
        ) as mock_delay:
            event._skip_webhook = True
            event.title = "via webhook"
            event.save()

        mock_delay.assert_not_called()

    def test_no_config_skips(self):
        company = CompanyFactory()
        # No CompanyWebhookConfig — webhooks aren't set up for this company.

        with patch(
            "modules.calendar.signals.fire_calendar_webhook.delay"
        ) as mock_delay:
            EventFactory(company=company, external_uid="uid-noconfig")

        mock_delay.assert_not_called()

    def test_disabled_config_skips(self):
        company = CompanyFactory()
        _setup_config(company, enabled=False)

        with patch(
            "modules.calendar.signals.fire_calendar_webhook.delay"
        ) as mock_delay:
            EventFactory(company=company, external_uid="uid-disabled")

        mock_delay.assert_not_called()
