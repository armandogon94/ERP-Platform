"""Tests for POST /api/v1/webhooks/calendar/<slug>/ (Slice 22).

Spec: docs/CALENDAR-SYNC-WEBHOOKS.md §Wire format, §Test plan.
Covers the 11 cases from §Test plan that don't require a live peer.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from core.factories import CompanyFactory
from core.models import CompanyWebhookConfig
from modules.calendar.factories import EventFactory
from modules.calendar.models import Event


SECRET = "0" * 64
URL_TEMPLATE = "/api/v1/webhooks/calendar/{slug}/"


def _sign(body: bytes, secret: str = SECRET) -> str:
    return "sha256=" + hmac.new(
        secret.encode(), body, hashlib.sha256
    ).hexdigest()


def _setup_config(company, *, enabled: bool = True, secret: str = SECRET):
    return CompanyWebhookConfig.objects.create(
        company=company,
        peer_url="https://peer.example.com/api/v1/webhooks/calendar/x/",
        shared_secret=secret,
        enabled=enabled,
    )


def _payload(
    *,
    external_uid: str = "uid-test-1",
    title: str = "Hello",
    updated_at=None,
    kind: str = "event.upserted",
    company_slug: str = "novapay",
):
    start = timezone.now()
    p = {
        "kind": kind,
        "company_external_id": company_slug,
        "payload": {
            "external_uid": external_uid,
            "title": title,
            "start_datetime": start.isoformat(),
            "end_datetime": (start + timedelta(hours=1)).isoformat(),
            "event_type": "meeting",
            "status": "confirmed",
            "all_day": False,
            "recurrence_rule": "",
            "attendees": [],
            "location": "",
        },
    }
    if updated_at:
        p["payload"]["updated_at"] = updated_at.isoformat()
    return p


def _post(api_client, slug, body_dict, *, source="crm", ts=None,
          delivery_id=None, secret=SECRET):
    body_bytes = json.dumps(body_dict).encode()
    headers = {
        "HTTP_X_WEBHOOK_SOURCE": source,
        "HTTP_X_WEBHOOK_TIMESTAMP": str(ts if ts is not None else int(time.time())),
        "HTTP_X_WEBHOOK_SIGNATURE": _sign(body_bytes, secret),
        "HTTP_X_WEBHOOK_DELIVERY_ID": delivery_id or str(uuid.uuid4()),
    }
    return api_client.post(
        URL_TEMPLATE.format(slug=slug),
        data=body_bytes,
        content_type="application/json",
        **headers,
    )


@pytest.mark.django_db
class TestReceiverHappyPath:
    def test_create_event_via_webhook(self, api_client):
        company = CompanyFactory(slug="novapay")
        _setup_config(company)

        body = _payload(updated_at=timezone.now())
        response = _post(api_client, "novapay", body)

        assert response.status_code == 200, response.content
        assert response.json()["result"] == "created"
        assert Event.objects.filter(
            company=company, external_uid="uid-test-1"
        ).count() == 1

    def test_update_via_lww_when_incoming_newer(self, api_client):
        company = CompanyFactory(slug="novapay")
        _setup_config(company)
        EventFactory(
            company=company, external_uid="uid-x", title="stored",
        )
        Event.objects.filter(external_uid="uid-x").update(
            updated_at=timezone.now() - timedelta(hours=1),
        )

        body = _payload(
            external_uid="uid-x",
            title="incoming",
            updated_at=timezone.now() + timedelta(minutes=1),
        )
        response = _post(api_client, "novapay", body)
        assert response.status_code == 200
        assert response.json()["result"] == "updated"

        Event.objects.get(external_uid="uid-x").title == "incoming"

    def test_lww_tie_keeps_stored(self, api_client):
        """REVIEW C-10 carries through to the webhook path."""
        company = CompanyFactory(slug="novapay")
        _setup_config(company)
        existing = EventFactory(
            company=company, external_uid="uid-tie", title="stored",
        )
        same_ts = timezone.now()
        Event.objects.filter(pk=existing.pk).update(updated_at=same_ts)

        body = _payload(
            external_uid="uid-tie", title="incoming", updated_at=same_ts,
        )
        response = _post(api_client, "novapay", body)
        assert response.status_code == 200
        assert response.json()["result"] == "skipped_lww"
        existing.refresh_from_db()
        assert existing.title == "stored"

    def test_event_deleted_kind_tombstones(self, api_client):
        company = CompanyFactory(slug="novapay")
        _setup_config(company)
        ev = EventFactory(
            company=company, external_uid="uid-del", status="confirmed",
        )

        body = {
            "kind": "event.deleted",
            "company_external_id": "novapay",
            "payload": {"external_uid": "uid-del"},
        }
        response = _post(api_client, "novapay", body)
        assert response.status_code == 200
        ev.refresh_from_db()
        assert ev.status == "cancelled"


@pytest.mark.django_db
class TestReceiverSecurity:
    def test_loop_guard_rejects_own_source(self, api_client):
        """Receiver MUST 400 if X-Webhook-Source equals our own name."""
        company = CompanyFactory(slug="novapay")
        _setup_config(company)
        body = _payload(updated_at=timezone.now())
        response = _post(api_client, "novapay", body, source="erp")
        assert response.status_code == 400
        assert "loop" in response.content.decode().lower() or "source" in response.content.decode().lower()

    def test_bad_signature_returns_401(self, api_client):
        company = CompanyFactory(slug="novapay")
        _setup_config(company, secret=SECRET)
        body_bytes = json.dumps(
            _payload(updated_at=timezone.now())
        ).encode()
        headers = {
            "HTTP_X_WEBHOOK_SOURCE": "crm",
            "HTTP_X_WEBHOOK_TIMESTAMP": str(int(time.time())),
            "HTTP_X_WEBHOOK_SIGNATURE": "sha256=" + "0" * 64,  # wrong
            "HTTP_X_WEBHOOK_DELIVERY_ID": str(uuid.uuid4()),
        }
        response = api_client.post(
            URL_TEMPLATE.format(slug="novapay"),
            data=body_bytes,
            content_type="application/json",
            **headers,
        )
        assert response.status_code == 401

    def test_missing_signature_returns_401(self, api_client):
        company = CompanyFactory(slug="novapay")
        _setup_config(company)
        body_bytes = json.dumps(
            _payload(updated_at=timezone.now())
        ).encode()
        response = api_client.post(
            URL_TEMPLATE.format(slug="novapay"),
            data=body_bytes,
            content_type="application/json",
            HTTP_X_WEBHOOK_SOURCE="crm",
            HTTP_X_WEBHOOK_TIMESTAMP=str(int(time.time())),
            HTTP_X_WEBHOOK_DELIVERY_ID=str(uuid.uuid4()),
            # No signature header.
        )
        assert response.status_code == 401

    def test_skewed_timestamp_returns_409(self, api_client):
        company = CompanyFactory(slug="novapay")
        _setup_config(company)
        body = _payload(updated_at=timezone.now())
        response = _post(
            api_client, "novapay", body,
            ts=int(time.time()) - 600,  # 10 min old
        )
        assert response.status_code == 409

    def test_url_slug_mismatch_returns_400(self, api_client):
        """Body's company_external_id must match URL slug."""
        company = CompanyFactory(slug="novapay")
        _setup_config(company)
        body = _payload(
            updated_at=timezone.now(),
            company_slug="different-slug",  # body says different
        )
        response = _post(api_client, "novapay", body)
        assert response.status_code == 400

    def test_unknown_company_slug_returns_404(self, api_client):
        body = _payload(updated_at=timezone.now(), company_slug="ghost")
        body_bytes = json.dumps(body).encode()
        response = api_client.post(
            URL_TEMPLATE.format(slug="ghost"),
            data=body_bytes,
            content_type="application/json",
            HTTP_X_WEBHOOK_SOURCE="crm",
            HTTP_X_WEBHOOK_TIMESTAMP=str(int(time.time())),
            HTTP_X_WEBHOOK_SIGNATURE=_sign(body_bytes),
            HTTP_X_WEBHOOK_DELIVERY_ID=str(uuid.uuid4()),
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestReceiverIdempotency:
    def test_duplicate_delivery_id_is_skipped(self, api_client):
        from django.core.cache import cache
        cache.clear()  # ensure clean

        company = CompanyFactory(slug="novapay")
        _setup_config(company)
        body = _payload(updated_at=timezone.now())
        delivery_id = str(uuid.uuid4())

        first = _post(api_client, "novapay", body, delivery_id=delivery_id)
        assert first.status_code == 200
        assert first.json()["result"] == "created"

        # Second POST with same Delivery-Id → no-op.
        second = _post(api_client, "novapay", body, delivery_id=delivery_id)
        assert second.status_code == 200
        assert second.json()["result"] == "skipped_duplicate"

        # Still only 1 event.
        assert Event.objects.filter(
            company=company, external_uid="uid-test-1"
        ).count() == 1


@pytest.mark.django_db
class TestReceiverConfig:
    def test_disabled_config_returns_404(self, api_client):
        """A company with no enabled config is invisible to webhooks."""
        company = CompanyFactory(slug="novapay")
        _setup_config(company, enabled=False)
        body = _payload(updated_at=timezone.now())
        response = _post(api_client, "novapay", body)
        # Disabled = treat as not configured for webhooks at all.
        assert response.status_code in (404, 401)

    def test_no_config_returns_404(self, api_client):
        CompanyFactory(slug="novapay")
        # No CompanyWebhookConfig at all.
        body = _payload(updated_at=timezone.now())
        response = _post(api_client, "novapay", body)
        assert response.status_code in (404, 401)
