"""HMAC + timestamp verification for cross-system webhooks (Slice 22).

Spec: docs/CALENDAR-SYNC-WEBHOOKS.md §HMAC computation, §Headers.

* ``verify_signature(raw_body, signature_header, shared_secret)`` —
  timing-safe HMAC-SHA256 verification of the ``X-Webhook-Signature``
  header against the raw request body. Returns ``True`` on a match.
* ``parse_signature_header(value)`` — strips the ``sha256=`` prefix the
  spec requires; returns ``None`` if absent.
* ``check_timestamp_skew(unix_ts, max_minutes=5)`` — returns ``True`` if
  the timestamp is within ±max_minutes of now. Defends against replay.

These helpers are deliberately stateless and free of Django imports so
they can be reused outside the request cycle (e.g. by the emitter
side's signing helper, or by tests of pure crypto behavior).
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Optional


def parse_signature_header(value: Optional[str]) -> Optional[str]:
    """Extract the hex digest from a ``sha256=<hex>`` header value.

    Returns ``None`` if the header is missing, empty, or not prefixed.
    Strict parsing — receivers MUST 401 on malformed headers.
    """
    if not value:
        return None
    if not value.startswith("sha256="):
        return None
    return value[len("sha256="):]


def compute_signature(raw_body: bytes, shared_secret: str) -> str:
    """Compute the hex HMAC-SHA256 used as ``X-Webhook-Signature`` value.

    Always returns just the hex digest (no ``sha256=`` prefix); callers
    add the prefix when assembling the header for outbound requests.
    """
    return hmac.new(
        shared_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()


def verify_signature(
    raw_body: bytes,
    signature_header: Optional[str],
    shared_secret: str,
) -> bool:
    """Return True iff ``signature_header`` matches HMAC-SHA256 of ``raw_body``.

    Timing-safe via ``hmac.compare_digest`` so failed verifications don't
    leak the correct prefix length via response time.
    """
    received = parse_signature_header(signature_header)
    if received is None:
        return False
    expected = compute_signature(raw_body, shared_secret)
    # ``compare_digest`` requires equal-length inputs; if a caller sends
    # a deliberately mis-sized signature we still want a constant-time
    # rejection, so coerce both sides to str and let it handle.
    return hmac.compare_digest(received, expected)


def check_timestamp_skew(unix_ts, max_minutes: int = 5) -> bool:
    """Return True iff ``unix_ts`` is within ±max_minutes of the current time.

    Accepts int or numeric string; returns ``False`` on None or unparseable
    input. Receivers MUST 409 if this returns False.
    """
    if unix_ts is None:
        return False
    try:
        ts = int(unix_ts)
    except (TypeError, ValueError):
        return False
    delta = abs(time.time() - ts)
    return delta <= max_minutes * 60
