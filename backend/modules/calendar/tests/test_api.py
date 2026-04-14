"""Tests for Calendar API endpoints."""
import pytest
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.calendar.factories import EventFactory, ResourceFactory
from modules.calendar.models import Event


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


# ─── Events ──────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestEventAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/calendar/events/")
        assert response.status_code == 401

    def test_list_returns_company_events(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        EventFactory(company=company, title="Team Standup")
        EventFactory(company=company, title="Sprint Review")
        auth(api_client, user)

        response = api_client.get("/api/v1/calendar/events/")
        assert response.status_code == 200
        titles = [e["title"] for e in response.json()]
        assert "Team Standup" in titles
        assert "Sprint Review" in titles

    def test_events_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        EventFactory(company=c1, title="Only C1 Event")
        EventFactory(company=c2, title="Only C2 Event")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/calendar/events/")
        titles = [e["title"] for e in response.json()]
        assert "Only C1 Event" in titles
        assert "Only C2 Event" not in titles

    def test_create_event(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        now = timezone.now()

        response = api_client.post(
            "/api/v1/calendar/events/",
            {
                "title": "New Meeting",
                "start_datetime": now.isoformat(),
                "end_datetime": (now + timezone.timedelta(hours=1)).isoformat(),
                "event_type": Event.EventType.MEETING,
                "status": Event.Status.CONFIRMED,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["title"] == "New Meeting"

    def test_retrieve_event(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        event = EventFactory(company=company, title="Board Meeting")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/calendar/events/{event.pk}/")
        assert response.status_code == 200
        assert response.json()["title"] == "Board Meeting"

    def test_update_event_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        event = EventFactory(company=company, status=Event.Status.CONFIRMED)
        auth(api_client, user)

        response = api_client.patch(
            f"/api/v1/calendar/events/{event.pk}/",
            {"status": Event.Status.CANCELLED},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == Event.Status.CANCELLED

    def test_cannot_access_other_company_event(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        event2 = EventFactory(company=c2)
        user1 = UserFactory(company=c1)
        auth(api_client, user1)

        response = api_client.get(f"/api/v1/calendar/events/{event2.pk}/")
        assert response.status_code == 404

    def test_filter_events_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        EventFactory(company=company, title="Confirmed", status=Event.Status.CONFIRMED)
        EventFactory(company=company, title="Cancelled", status=Event.Status.CANCELLED)
        auth(api_client, user)

        response = api_client.get(
            "/api/v1/calendar/events/", {"status": Event.Status.CONFIRMED}
        )
        assert response.status_code == 200
        titles = [e["title"] for e in response.json()]
        assert "Confirmed" in titles
        assert "Cancelled" not in titles

    def test_filter_events_updated_since(self, api_client):
        """Polling endpoint for CRM sync."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        EventFactory(company=company, title="Old Event")
        auth(api_client, user)

        past = (timezone.now() - timezone.timedelta(days=30)).isoformat()
        response = api_client.get(
            "/api/v1/calendar/events/", {"updated_since": past}
        )
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_event_response_includes_attendee_count(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        event = EventFactory(company=company)
        auth(api_client, user)

        response = api_client.get(f"/api/v1/calendar/events/{event.pk}/")
        assert response.status_code == 200
        assert "attendee_count" in response.json()


# ─── Resources ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestResourceAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/calendar/resources/")
        assert response.status_code == 401

    def test_list_returns_company_resources(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        ResourceFactory(company=company, name="Room A")
        ResourceFactory(company=company, name="Projector B")
        auth(api_client, user)

        response = api_client.get("/api/v1/calendar/resources/")
        assert response.status_code == 200
        names = [r["name"] for r in response.json()]
        assert "Room A" in names
        assert "Projector B" in names

    def test_resources_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        ResourceFactory(company=c1, name="C1 Room")
        ResourceFactory(company=c2, name="C2 Room")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/calendar/resources/")
        names = [r["name"] for r in response.json()]
        assert "C1 Room" in names
        assert "C2 Room" not in names

    def test_create_resource(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/calendar/resources/",
            {"name": "Dental Chair 1", "resource_type": "room", "capacity": 1},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Dental Chair 1"
