"""Shared business-logic services for the calendar module.

Extracts the LWW upsert + tombstone logic from the polling viewset so
both the polling endpoint (Slice 18) and the webhook receiver
(Slice 22) use the same code path. Saves on the model are flagged with
``_skip_webhook=True`` when called from the receiver so the post_save
emitter doesn't loop the change back to the peer.

Spec: docs/CALENDAR-SYNC-WEBHOOKS.md §LWW conflict resolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from django.utils.dateparse import parse_datetime

from modules.calendar.models import Event


def parse_updated_at(raw: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp tolerating URL-quoted ``+`` as space.

    Returns ``None`` on missing or unparseable input. Callers decide how
    to surface the failure (400 from polling, 400 from webhook).
    """
    if not raw:
        return None
    fixed = raw.replace(" ", "+")
    return parse_datetime(fixed)


@dataclass
class UpsertResult:
    """Outcome of a single-event upsert operation.

    ``status`` is one of ``"created"``, ``"updated"``, ``"skipped_lww"``.
    ``event`` is the post-operation Event instance (or the stored one on
    skip). ``error`` is set when the upsert was rejected for input
    reasons; receiver maps it to a 400.
    """

    status: str
    event: Optional[Event] = None
    error: Optional[dict] = None


def upsert_event(
    *,
    company,
    payload: dict[str, Any],
    skip_webhook: bool = False,
) -> UpsertResult:
    """Run the LWW upsert for a single event payload, scoped to ``company``.

    See docs/CALENDAR-SYNC-WEBHOOKS.md §LWW conflict resolution for the
    rules. ``skip_webhook=True`` flags the saved instance so the
    post_save emitter signal short-circuits — used by the webhook
    receiver to prevent infinite loops.
    """
    from modules.calendar.serializers import EventSerializer

    external_uid = payload.get("external_uid")

    # No external_uid → plain create.
    if not external_uid:
        serializer = EventSerializer(data=payload)
        if not serializer.is_valid():
            return UpsertResult(status="error", error=serializer.errors)
        event = serializer.save(company=company)
        if skip_webhook:
            event._skip_webhook = True
            event.save(update_fields=[])  # no-op save just to mark? Skip.
        return UpsertResult(status="created", event=event)

    existing = Event.objects.filter(
        company=company, external_uid=external_uid
    ).first()

    if existing is None:
        serializer = EventSerializer(data=payload)
        if not serializer.is_valid():
            return UpsertResult(status="error", error=serializer.errors)
        event = serializer.save(company=company)
        if skip_webhook:
            # Re-save with the flag set so post_save sees it.
            event._skip_webhook = True
            event.save(update_fields=["updated_at"])
        return UpsertResult(status="created", event=event)

    # Collision path — updated_at REQUIRED for LWW.
    raw_updated = payload.get("updated_at")
    if not raw_updated:
        return UpsertResult(
            status="error",
            error={
                "updated_at": (
                    "Required on upsert against existing external_uid "
                    "(last-write-wins)."
                )
            },
        )
    incoming_updated = parse_updated_at(raw_updated)
    if incoming_updated is None:
        return UpsertResult(
            status="error",
            error={"updated_at": f"Unparseable ISO-8601 timestamp: {raw_updated!r}"},
        )

    # Tie preserves stored (REVIEW C-10).
    if incoming_updated <= existing.updated_at:
        return UpsertResult(status="skipped_lww", event=existing)

    serializer = EventSerializer(existing, data=payload, partial=True)
    if not serializer.is_valid():
        return UpsertResult(status="error", error=serializer.errors)
    event = serializer.save()
    if skip_webhook:
        event._skip_webhook = True
        event.save(update_fields=["updated_at"])
    return UpsertResult(status="updated", event=event)


def tombstone_event(
    *,
    company,
    external_uid: str,
    skip_webhook: bool = False,
) -> UpsertResult:
    """Soft-delete an event by setting ``status='cancelled'``.

    Implements the ``kind: "event.deleted"`` webhook semantics (no hard
    DB delete; matches polling-spec deletion strategy at
    docs/CALENDAR-SYNC-POLLING.md §Deletes).

    Idempotent: tombstoning an already-cancelled event returns
    ``skipped_lww``. Tombstoning a missing event returns
    ``status="created"`` with ``event=None`` so the receiver can map it
    to a 200 — the peer's intent (this UID is gone) is respected even
    if we never knew about it.
    """
    if not external_uid:
        return UpsertResult(
            status="error",
            error={"external_uid": "Required for event.deleted."},
        )

    event = Event.objects.filter(
        company=company, external_uid=external_uid
    ).first()
    if event is None:
        # Treat as a no-op success — peer says "this UID is gone";
        # we never had it.
        return UpsertResult(status="skipped_lww", event=None)

    if event.status == "cancelled":
        return UpsertResult(status="skipped_lww", event=event)

    event.status = "cancelled"
    if skip_webhook:
        event._skip_webhook = True
    event.save(update_fields=["status", "updated_at"])
    return UpsertResult(status="updated", event=event)
