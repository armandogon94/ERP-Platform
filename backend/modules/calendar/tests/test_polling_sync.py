"""Tests for the calendar polling-sync contract (Slice 18, D27)."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.calendar.factories import EventFactory
from modules.calendar.models import Event


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


def _event_payload(
    *, external_uid: str, title: str, updated_at=None, start=None
):
    start = start or timezone.now()
    body = {
        "title": title,
        "start_datetime": start.isoformat(),
        "end_datetime": (start + timedelta(hours=1)).isoformat(),
        "event_type": "meeting",
        "external_uid": external_uid,
    }
    if updated_at:
        body["updated_at"] = updated_at.isoformat()
    return body


@pytest.mark.django_db
class TestUpdatedSinceFilter:
    def test_returns_events_updated_since(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        # Two events, simulate one being "older" by stamping updated_at manually.
        old = EventFactory(company=company, title="Old", external_uid="uid-old")
        recent = EventFactory(
            company=company, title="Recent", external_uid="uid-recent"
        )
        # Force updated_at ordering
        Event.objects.filter(pk=old.pk).update(
            updated_at=timezone.now() - timedelta(days=2)
        )
        Event.objects.filter(pk=recent.pk).update(
            updated_at=timezone.now()
        )
        auth(api_client, user)

        since = (timezone.now() - timedelta(days=1)).isoformat()
        response = api_client.get(f"/api/v1/calendar/events/?updated_since={since}")
        assert response.status_code == 200
        titles = [e["title"] for e in response.json()]
        assert "Recent" in titles
        assert "Old" not in titles

    def test_response_includes_external_uid(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        EventFactory(company=company, external_uid="uid-1", title="E1")
        auth(api_client, user)
        response = api_client.get("/api/v1/calendar/events/")
        body = response.json()
        assert any(e.get("external_uid") == "uid-1" for e in body)


@pytest.mark.django_db
class TestUpsertByExternalUID:
    def test_create_with_new_external_uid(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/calendar/events/",
            _event_payload(external_uid="uid-new", title="First"),
            format="json",
        )
        assert response.status_code == 201, response.content
        assert Event.objects.filter(
            company=company, external_uid="uid-new"
        ).count() == 1

    def test_repost_same_uid_upserts_not_duplicates(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        api_client.post(
            "/api/v1/calendar/events/",
            _event_payload(
                external_uid="uid-x", title="v1", updated_at=timezone.now()
            ),
            format="json",
        )
        # Use a timestamp strictly in the future so LWW picks the new payload.
        response = api_client.post(
            "/api/v1/calendar/events/",
            _event_payload(
                external_uid="uid-x",
                title="v2",
                updated_at=timezone.now() + timedelta(minutes=5),
            ),
            format="json",
        )
        # Either 200 (updated) or 201 (created) is acceptable, but not an error.
        assert response.status_code in (200, 201), response.content
        assert Event.objects.filter(
            company=company, external_uid="uid-x"
        ).count() == 1
        event = Event.objects.get(company=company, external_uid="uid-x")
        assert event.title == "v2"

    def test_upsert_rejects_missing_updated_at(self, api_client):
        """REVIEW I-2: an upsert that collides with a stored external_uid
        MUST include updated_at — otherwise LWW is undefined."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        EventFactory(company=company, external_uid="uid-i2", title="stored")
        auth(api_client, user)

        payload = _event_payload(external_uid="uid-i2", title="no timestamp")
        payload.pop("updated_at", None)
        response = api_client.post(
            "/api/v1/calendar/events/", payload, format="json"
        )
        assert response.status_code == 400
        assert "updated_at" in response.json()

    def test_updated_since_unparseable_returns_400(self, api_client):
        """REVIEW I-5: malformed ?updated_since must 400, not silently return
        the full set."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.get(
            "/api/v1/calendar/events/?updated_since=not-a-date"
        )
        assert response.status_code == 400
        assert "updated_since" in response.json()

    def test_lww_tie_prefers_stored(self, api_client):
        """REVIEW C-10: when incoming.updated_at == stored.updated_at, the
        stored record wins (no silent overwrite on a tie — see D27 LWW spec)."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        existing = EventFactory(
            company=company,
            external_uid="uid-tie",
            title="stored",
        )
        tie_time = timezone.now()
        Event.objects.filter(pk=existing.pk).update(updated_at=tie_time)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/calendar/events/",
            _event_payload(
                external_uid="uid-tie",
                title="incoming (same timestamp)",
                updated_at=tie_time,
            ),
            format="json",
        )
        assert response.status_code in (200, 201, 409)
        existing.refresh_from_db()
        assert existing.title == "stored", (
            "Tie on updated_at must preserve stored record; got "
            f"'{existing.title}' after upsert"
        )

    def test_lww_older_update_ignored(self, api_client):
        """If the incoming payload's updated_at is older than the stored
        record's updated_at, the stored version wins (last-write-wins)."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        # Pre-existing event updated just now with v2
        existing = EventFactory(
            company=company,
            external_uid="uid-lww",
            title="v2 (stored)",
        )
        # Force its updated_at to be "now"
        Event.objects.filter(pk=existing.pk).update(updated_at=timezone.now())
        auth(api_client, user)

        # Client sends an older version
        older_time = timezone.now() - timedelta(hours=1)
        response = api_client.post(
            "/api/v1/calendar/events/",
            _event_payload(
                external_uid="uid-lww",
                title="v1 (older)",
                updated_at=older_time,
            ),
            format="json",
        )
        assert response.status_code in (200, 201, 409)
        existing.refresh_from_db()
        assert existing.title == "v2 (stored)"


@pytest.mark.django_db
class TestBulkEndpoint:
    def test_bulk_accepts_array(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        start = timezone.now()
        payload = [
            _event_payload(external_uid=f"uid-{i}", title=f"E{i}", start=start)
            for i in range(5)
        ]
        response = api_client.post(
            "/api/v1/calendar/events/bulk/", payload, format="json"
        )
        assert response.status_code == 200, response.content
        body = response.json()
        assert body["created"] + body["updated"] == 5
        assert Event.objects.filter(company=company).count() == 5

    def test_bulk_rejects_over_500(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        start = timezone.now()
        payload = [
            _event_payload(external_uid=f"uid-{i}", title=f"E{i}", start=start)
            for i in range(501)
        ]
        response = api_client.post(
            "/api/v1/calendar/events/bulk/", payload, format="json"
        )
        assert response.status_code == 400

    def test_bulk_second_call_updates_not_duplicates(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        start = timezone.now()
        # updated_at field is auto_now=True on the server — client values are
        # ignored for storage but still inform LWW. Use future timestamps to
        # simulate "newer than stored" without flaking on sub-second timing.
        t_now = timezone.now()
        batch = [
            _event_payload(external_uid="uid-a", title="A", start=start, updated_at=t_now),
            _event_payload(external_uid="uid-b", title="B", start=start, updated_at=t_now),
        ]
        api_client.post("/api/v1/calendar/events/bulk/", batch, format="json")
        # Second call: payload carries an updated_at clearly in the future so
        # LWW picks "incoming strictly newer than stored".
        t_future = timezone.now() + timedelta(minutes=5)
        batch_two = [
            _event_payload(external_uid="uid-a", title="A-updated", start=start, updated_at=t_future),
            _event_payload(external_uid="uid-c", title="C", start=start, updated_at=t_future),
        ]
        response = api_client.post(
            "/api/v1/calendar/events/bulk/", batch_two, format="json"
        )
        body = response.json()
        assert body["created"] == 1
        assert body["updated"] == 1
        assert Event.objects.filter(company=company).count() == 3
        updated = Event.objects.get(company=company, external_uid="uid-a")
        assert updated.title == "A-updated"
