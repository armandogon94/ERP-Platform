"""POST /api/v1/webhooks/calendar/<company_slug>/ — receive cross-system events.

Spec: docs/CALENDAR-SYNC-WEBHOOKS.md.

This endpoint is **HMAC-only** — no JWT/session auth. Authentication is
the per-company shared secret in ``CompanyWebhookConfig.shared_secret``.

Request flow (each step on failure returns the documented status code):

1. Look up ``CompanyWebhookConfig`` for the URL slug. Missing or
   ``enabled=False`` → 404.
2. Reject loops: if ``X-Webhook-Source`` equals our own name → 400.
3. Reject skewed timestamps (>5 min) → 409.
4. Verify HMAC-SHA256 signature against the raw body → 401 on fail.
5. Parse JSON. If ``company_external_id`` (body) ≠ URL slug → 400.
6. Dedupe on ``X-Webhook-Delivery-Id`` via Redis (24h TTL) → 200
   ``{"result": "skipped_duplicate"}`` on a hit.
7. Dispatch by ``kind``:
   * ``event.upserted`` → LWW upsert via ``services.upsert_event`` with
     ``skip_webhook=True`` so the post_save emitter doesn't loop the
     change back to the peer. Returns 200 ``created|updated|skipped_lww``.
   * ``event.deleted`` → tombstone via
     ``services.tombstone_event``. Returns 200.
"""

from __future__ import annotations

import json

from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.v1.webhook_security import (
    check_timestamp_skew,
    verify_signature,
)
from core.models import Company, CompanyWebhookConfig
from modules.calendar.services import tombstone_event, upsert_event


OWN_SOURCE = "erp"
ALLOWED_KINDS = {"event.upserted", "event.deleted"}
DEDUP_TTL_SECONDS = 24 * 60 * 60


def _err(detail, status):
    return Response({"detail": detail}, status=status)


@api_view(["POST"])
@permission_classes([AllowAny])  # HMAC is the auth layer.
def calendar_webhook(request, slug: str):
    # ── (1) Tenant + config lookup ───────────────────────────────────
    try:
        company = Company.objects.get(slug=slug)
    except Company.DoesNotExist:
        return _err(f"Unknown company slug: {slug}", status=404)
    try:
        config = company.webhook_config
    except CompanyWebhookConfig.DoesNotExist:
        return _err("Webhook not configured for this company.", status=404)
    if not config.enabled:
        return _err("Webhook disabled for this company.", status=404)

    # ── (2) Loop guard ──────────────────────────────────────────────
    source = request.META.get("HTTP_X_WEBHOOK_SOURCE", "")
    if not source:
        return _err("Missing X-Webhook-Source.", status=400)
    if source == OWN_SOURCE:
        return _err(
            "Loop detected: X-Webhook-Source equals our own name. "
            "Inbound webhook from peer must not declare source=erp.",
            status=400,
        )

    # ── (3) Timestamp skew ──────────────────────────────────────────
    ts = request.META.get("HTTP_X_WEBHOOK_TIMESTAMP")
    if not check_timestamp_skew(ts):
        return _err(
            "X-Webhook-Timestamp missing or > 5 minutes from now.",
            status=409,
        )

    # ── (4) HMAC verification on the RAW body ───────────────────────
    raw_body: bytes = request.body
    sig_header = request.META.get("HTTP_X_WEBHOOK_SIGNATURE")
    if not verify_signature(raw_body, sig_header, config.shared_secret):
        return _err("Invalid HMAC signature.", status=401)

    # ── (5) Parse + slug-mismatch assertion ─────────────────────────
    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        return _err("Body is not valid JSON.", status=400)

    body_slug = body.get("company_external_id")
    if body_slug != slug:
        return _err(
            "company_external_id in body must match URL slug "
            f"(got {body_slug!r}, URL says {slug!r}).",
            status=400,
        )

    kind = body.get("kind")
    if kind not in ALLOWED_KINDS:
        return _err(f"Unsupported kind: {kind!r}", status=400)

    payload = body.get("payload") or {}
    if not isinstance(payload, dict):
        return _err("payload must be an object.", status=400)

    # ── (6) Idempotency dedupe ──────────────────────────────────────
    delivery_id = request.META.get("HTTP_X_WEBHOOK_DELIVERY_ID")
    if not delivery_id:
        return _err("Missing X-Webhook-Delivery-Id.", status=400)
    cache_key = f"webhook_seen:{slug}:{delivery_id}"
    if cache.get(cache_key) is not None:
        return Response({"result": "skipped_duplicate"}, status=200)

    # ── (7) Dispatch ────────────────────────────────────────────────
    if kind == "event.upserted":
        result = upsert_event(
            company=company, payload=payload, skip_webhook=True,
        )
    else:  # event.deleted
        external_uid = payload.get("external_uid")
        result = tombstone_event(
            company=company,
            external_uid=external_uid,
            skip_webhook=True,
        )

    if result.status == "error":
        return Response({"errors": result.error}, status=400)

    # Mark this delivery as processed (24h TTL).
    cache.set(cache_key, "1", timeout=DEDUP_TTL_SECONDS)

    return Response({"result": result.status}, status=200)
