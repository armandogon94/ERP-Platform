"""Outbound webhook emitter for the calendar module (Slice 22).

Spec: docs/CALENDAR-SYNC-WEBHOOKS.md §Retry policy, §Wire format.

The ``fire_calendar_webhook`` Celery task is enqueued from the post_save
signal on ``Event`` (see ``signals.py``). It:

1. Loads the Event + the company's ``CompanyWebhookConfig``.
2. Skips silently if the config is missing, disabled, or has no peer URL.
3. Builds the spec-shaped envelope + signs the raw body.
4. POSTs to the peer with retry semantics matching the spec
   (``autoretry_for``, exponential backoff, max 5 retries).
5. Records success / error timestamps on the config row.

Loop prevention: the signal that enqueues this task already checks for
``instance._skip_webhook`` so receiver-driven saves never reach this
task. This is the belt; the receiver also asserts ``X-Webhook-Source``
(via the spec's loop-guard rule) — that's the braces.
"""

from __future__ import annotations

import json
import time
import uuid

import requests
from celery import shared_task
from django.utils import timezone

from api.v1.webhook_security import compute_signature

OWN_SOURCE = "erp"
TIMEOUT_SECONDS = 10


def _build_payload(event, kind: str) -> dict:
    """Translate an Event into the wire-format payload (spec §Body)."""
    if kind == "event.deleted":
        # Tombstone — minimal payload is fine; receiver only needs the UID.
        return {"external_uid": event.external_uid}

    return {
        "external_uid": event.external_uid,
        "title": event.title,
        "start_datetime": event.start_datetime.isoformat()
        if event.start_datetime else None,
        "end_datetime": event.end_datetime.isoformat()
        if event.end_datetime else None,
        "event_type": event.event_type,
        "status": event.status,
        "all_day": getattr(event, "all_day", False),
        "recurrence_rule": getattr(event, "recurrence_rule", "") or "",
        "attendees": [],  # TODO: populate when attendee sync lands
        "location": getattr(event, "location", "") or "",
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
    }


def _build_envelope(event, kind: str) -> dict:
    return {
        "kind": kind,
        "company_external_id": event.company.slug,
        "payload": _build_payload(event, kind),
    }


@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException, requests.Timeout),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
)
def fire_calendar_webhook(self, event_id: int, kind: str) -> dict:
    """Send a single calendar webhook to the company's configured peer.

    Returns a small dict for diagnostics. Idempotent w.r.t. retries —
    a retry uses the same Delivery-Id, and the receiver dedupes via
    Redis.
    """
    from core.models import CompanyWebhookConfig
    from modules.calendar.models import Event

    try:
        event = Event.objects.select_related("company").get(pk=event_id)
    except Event.DoesNotExist:
        # Race: emitter triggered, then the event was hard-deleted.
        # Nothing to send.
        return {"skipped": "event_missing"}

    try:
        config = event.company.webhook_config
    except CompanyWebhookConfig.DoesNotExist:
        return {"skipped": "no_config"}

    if not config.enabled or not config.peer_url:
        return {"skipped": "disabled_or_no_peer"}

    # Build + sign.
    envelope = _build_envelope(event, kind)
    body = json.dumps(envelope).encode()
    signature = compute_signature(body, config.shared_secret)

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Source": OWN_SOURCE,
        "X-Webhook-Timestamp": str(int(time.time())),
        "X-Webhook-Signature": f"sha256={signature}",
        # On retry, ``self.request.id`` would change but a stable
        # Delivery-Id keeps idempotency. For first-shot we generate
        # once; for retries Celery preserves args, so we'd want a
        # deterministic ID. Use (event_id, kind, body-hash) for
        # determinism across retries.
        "X-Webhook-Delivery-Id": _delivery_id(event_id, kind, body),
    }

    try:
        response = requests.post(
            config.peer_url,
            data=body,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        config.last_error_at = timezone.now()
        config.last_error_message = f"{type(exc).__name__}: {exc}"
        config.save(update_fields=["last_error_at", "last_error_message"])
        raise  # let Celery autoretry pick this up

    if 200 <= response.status_code < 300:
        config.last_success_at = timezone.now()
        config.save(update_fields=["last_success_at"])
        return {"sent": True, "status": response.status_code}

    # Peer returned an error. 4xx = no retry (config issue; sender
    # should fix and resend). 5xx = retry until exhausted.
    config.last_error_at = timezone.now()
    config.last_error_message = (
        f"HTTP {response.status_code}: {response.text[:500]}"
    )
    config.save(update_fields=["last_error_at", "last_error_message"])

    if 500 <= response.status_code < 600:
        # Trigger retry. Celery will autoretry on RequestException, so
        # raise one to keep the same code path.
        raise requests.RequestException(f"Peer 5xx: {response.status_code}")

    return {"sent": False, "status": response.status_code}


def _delivery_id(event_id: int, kind: str, body: bytes) -> str:
    """Deterministic Delivery-Id so Celery retries don't bypass dedupe.

    Receiver sees the same key on every retry → second-onwards return
    ``skipped_duplicate`` instead of duplicating writes.
    """
    import hashlib

    seed = f"{event_id}:{kind}:".encode() + body
    digest = hashlib.sha256(seed).digest()[:16]
    return str(uuid.UUID(bytes=digest))
