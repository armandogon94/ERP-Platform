"""Tests for the outbound webhook emitter (Slice 22).

Spec: docs/CALENDAR-SYNC-WEBHOOKS.md §Retry policy, §Wire format.
"""

from __future__ import annotations

import json
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from core.factories import CompanyFactory
from core.models import CompanyWebhookConfig
from modules.calendar.factories import EventFactory


def _setup(*, enabled: bool = True):
    company = CompanyFactory(slug="novapay")
    cfg = CompanyWebhookConfig.objects.create(
        company=company,
        peer_url="https://crm.example.com/api/v1/webhooks/calendar/novapay/",
        shared_secret="0" * 64,
        enabled=enabled,
    )
    event = EventFactory(
        company=company,
        external_uid="uid-emit",
        title="Outbound test",
    )
    return company, cfg, event


@pytest.mark.django_db
class TestEmitterDispatch:
    def test_skips_when_config_disabled(self):
        from modules.calendar.tasks import fire_calendar_webhook

        company, cfg, event = _setup(enabled=False)
        with patch("modules.calendar.tasks.requests.post") as mock_post:
            fire_calendar_webhook(event.pk, "event.upserted")
        mock_post.assert_not_called()

    def test_skips_when_no_config(self):
        from modules.calendar.tasks import fire_calendar_webhook

        company = CompanyFactory(slug="novapay")
        event = EventFactory(company=company, external_uid="uid-x")
        # No CompanyWebhookConfig at all.
        with patch("modules.calendar.tasks.requests.post") as mock_post:
            fire_calendar_webhook(event.pk, "event.upserted")
        mock_post.assert_not_called()

    def test_posts_signed_request_to_peer(self):
        from modules.calendar.tasks import fire_calendar_webhook

        company, cfg, event = _setup()
        with patch("modules.calendar.tasks.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.text = ""
            fire_calendar_webhook(event.pk, "event.upserted")

        assert mock_post.called
        url, *_ = mock_post.call_args.args
        kwargs = mock_post.call_args.kwargs
        assert url == cfg.peer_url
        # All four required headers present.
        headers = kwargs.get("headers") or {}
        assert headers.get("X-Webhook-Source") == "erp"
        assert "X-Webhook-Timestamp" in headers
        assert "X-Webhook-Signature" in headers
        assert headers["X-Webhook-Signature"].startswith("sha256=")
        assert "X-Webhook-Delivery-Id" in headers
        # Body matches spec shape.
        body = kwargs.get("data")
        assert body is not None
        parsed = json.loads(body)
        assert parsed["kind"] == "event.upserted"
        assert parsed["company_external_id"] == "novapay"
        assert parsed["payload"]["external_uid"] == "uid-emit"
        assert parsed["payload"]["title"] == "Outbound test"

    def test_signature_matches_body(self):
        """Signature in header MUST be HMAC-SHA256 of the actual body bytes."""
        import hashlib
        import hmac
        from modules.calendar.tasks import fire_calendar_webhook

        company, cfg, event = _setup()
        with patch("modules.calendar.tasks.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.text = ""
            fire_calendar_webhook(event.pk, "event.upserted")

        kwargs = mock_post.call_args.kwargs
        body = kwargs["data"].encode() if isinstance(kwargs["data"], str) else kwargs["data"]
        sig_hex = kwargs["headers"]["X-Webhook-Signature"][len("sha256="):]
        expected = hmac.new(cfg.shared_secret.encode(), body, hashlib.sha256).hexdigest()
        assert sig_hex == expected

    def test_event_deleted_kind_emits_minimal_payload(self):
        from modules.calendar.tasks import fire_calendar_webhook

        company, cfg, event = _setup()
        with patch("modules.calendar.tasks.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.text = ""
            fire_calendar_webhook(event.pk, "event.deleted")

        kwargs = mock_post.call_args.kwargs
        parsed = json.loads(kwargs["data"])
        assert parsed["kind"] == "event.deleted"
        # Minimal: external_uid is enough to tombstone.
        assert parsed["payload"]["external_uid"] == "uid-emit"


@pytest.mark.django_db
class TestEmitterStatusTracking:
    def test_records_success_on_200(self):
        from modules.calendar.tasks import fire_calendar_webhook

        company, cfg, event = _setup()
        with patch("modules.calendar.tasks.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.text = ""
            fire_calendar_webhook(event.pk, "event.upserted")

        cfg.refresh_from_db()
        assert cfg.last_success_at is not None
        assert cfg.last_error_at is None

    def test_records_error_on_5xx(self):
        from modules.calendar.tasks import fire_calendar_webhook

        company, cfg, event = _setup()
        with patch("modules.calendar.tasks.requests.post") as mock_post:
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = "internal server error"
            # The synchronous call path captures the failure into the
            # config row; Celery retry semantics are outside this test
            # (we don't run the actual broker).
            try:
                fire_calendar_webhook(event.pk, "event.upserted")
            except Exception:
                pass  # retries would be raised by Celery infra

        cfg.refresh_from_db()
        assert cfg.last_error_at is not None
        assert "500" in cfg.last_error_message
