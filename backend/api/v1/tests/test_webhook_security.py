"""Tests for HMAC + timestamp verification helpers (Slice 22).

Spec: docs/CALENDAR-SYNC-WEBHOOKS.md §HMAC computation, §Headers.
"""

import hashlib
import hmac
import time

import pytest


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


class TestParseSignatureHeader:
    def test_strips_sha256_prefix(self):
        from api.v1.webhook_security import parse_signature_header

        assert parse_signature_header("sha256=deadbeef") == "deadbeef"

    def test_returns_none_for_missing_prefix(self):
        from api.v1.webhook_security import parse_signature_header

        assert parse_signature_header("deadbeef") is None

    def test_returns_none_for_empty(self):
        from api.v1.webhook_security import parse_signature_header

        assert parse_signature_header("") is None
        assert parse_signature_header(None) is None


class TestVerifySignature:
    def test_valid_signature_passes(self):
        from api.v1.webhook_security import verify_signature

        body = b'{"hello":"world"}'
        secret = "0" * 64
        sig = _sign(body, secret)
        assert verify_signature(body, f"sha256={sig}", secret) is True

    def test_wrong_secret_fails(self):
        from api.v1.webhook_security import verify_signature

        body = b'{"hello":"world"}'
        good_secret = "0" * 64
        sig = _sign(body, good_secret)
        # Verify with a different secret → fails.
        assert verify_signature(body, f"sha256={sig}", "1" * 64) is False

    def test_tampered_body_fails(self):
        from api.v1.webhook_security import verify_signature

        secret = "0" * 64
        sig = _sign(b'{"hello":"world"}', secret)
        # Verify against tampered body → fails.
        assert (
            verify_signature(b'{"hello":"WORLD"}', f"sha256={sig}", secret) is False
        )

    def test_missing_signature_fails(self):
        from api.v1.webhook_security import verify_signature

        body = b'{}'
        secret = "0" * 64
        assert verify_signature(body, "", secret) is False
        assert verify_signature(body, None, secret) is False

    def test_malformed_signature_fails(self):
        from api.v1.webhook_security import verify_signature

        body = b'{}'
        secret = "0" * 64
        # No "sha256=" prefix.
        assert verify_signature(body, "deadbeef", secret) is False


class TestCheckTimestampSkew:
    def test_now_is_in_window(self):
        from api.v1.webhook_security import check_timestamp_skew

        assert check_timestamp_skew(int(time.time())) is True

    def test_4_minutes_old_is_in_window(self):
        from api.v1.webhook_security import check_timestamp_skew

        assert check_timestamp_skew(int(time.time()) - 4 * 60) is True

    def test_6_minutes_old_is_rejected(self):
        from api.v1.webhook_security import check_timestamp_skew

        assert check_timestamp_skew(int(time.time()) - 6 * 60) is False

    def test_6_minutes_in_future_is_rejected(self):
        from api.v1.webhook_security import check_timestamp_skew

        assert check_timestamp_skew(int(time.time()) + 6 * 60) is False

    def test_none_is_rejected(self):
        from api.v1.webhook_security import check_timestamp_skew

        assert check_timestamp_skew(None) is False

    def test_unparseable_string_is_rejected(self):
        from api.v1.webhook_security import check_timestamp_skew

        assert check_timestamp_skew("not-a-number") is False
