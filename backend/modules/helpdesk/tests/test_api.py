"""API tests for the Helpdesk module (Slice 15)."""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.helpdesk.factories import (
    KnowledgeArticleFactory,
    SLAConfigFactory,
    TicketCategoryFactory,
    TicketFactory,
)
from modules.helpdesk.models import Ticket


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestTicketCategoryAPI:
    def test_list_requires_auth(self, api_client):
        assert api_client.get("/api/v1/helpdesk/categories/").status_code == 401

    def test_create(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/helpdesk/categories/",
            {"name": "Billing", "sla_hours": 48},
            format="json",
        )
        assert response.status_code == 201, response.content


@pytest.mark.django_db
class TestTicketAPI:
    def test_create_auto_number(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/helpdesk/tickets/",
            {"title": "Login broken", "priority": "high"},
            format="json",
        )
        assert response.status_code == 201, response.content
        body = response.json()
        assert body["ticket_number"].startswith("TKT/")
        assert body["status"] == "new"

    def test_filter_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        TicketFactory(company=company, title="Open1", status="new")
        TicketFactory(company=company, title="Done1", status="resolved")
        auth(api_client, user)
        response = api_client.get("/api/v1/helpdesk/tickets/?status=new")
        titles = [t["title"] for t in response.json()]
        assert titles == ["Open1"]

    def test_filter_by_category(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        cat = TicketCategoryFactory(company=company, name="Billing")
        TicketFactory(company=company, category=cat, title="C1")
        TicketFactory(company=company, title="C2")
        auth(api_client, user)
        response = api_client.get(
            f"/api/v1/helpdesk/tickets/?category={cat.id}"
        )
        titles = [t["title"] for t in response.json()]
        assert titles == ["C1"]

    def test_resolve_action(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        t = TicketFactory(company=company, status="in_progress")
        auth(api_client, user)
        response = api_client.post(
            f"/api/v1/helpdesk/tickets/{t.pk}/resolve/"
        )
        assert response.status_code == 200, response.content
        t.refresh_from_db()
        assert t.status == Ticket.Status.RESOLVED
        assert t.resolved_at is not None

    def test_resolve_rejects_already_closed(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        t = TicketFactory(company=company, status="closed")
        auth(api_client, user)
        response = api_client.post(
            f"/api/v1/helpdesk/tickets/{t.pk}/resolve/"
        )
        assert response.status_code == 400

    def test_reopen_action(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        t = TicketFactory(company=company, status="resolved")
        auth(api_client, user)
        response = api_client.post(
            f"/api/v1/helpdesk/tickets/{t.pk}/reopen/"
        )
        assert response.status_code == 200, response.content
        t.refresh_from_db()
        assert t.status == Ticket.Status.IN_PROGRESS
        assert t.resolved_at is None


@pytest.mark.django_db
class TestSLAConfigAPI:
    def test_filter_by_category(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        cat1 = TicketCategoryFactory(company=company, name="A")
        cat2 = TicketCategoryFactory(company=company, name="B")
        SLAConfigFactory(company=company, category=cat1)
        SLAConfigFactory(company=company, category=cat2)
        auth(api_client, user)
        response = api_client.get(
            f"/api/v1/helpdesk/sla-configs/?category={cat1.id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.django_db
class TestKnowledgeArticleAPI:
    def test_filter_by_published(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        KnowledgeArticleFactory(
            company=company, title="Draft1", slug="d1", published=False
        )
        KnowledgeArticleFactory(
            company=company, title="Pub1", slug="p1", published=True
        )
        auth(api_client, user)
        response = api_client.get("/api/v1/helpdesk/articles/?published=true")
        titles = [a["title"] for a in response.json()]
        assert titles == ["Pub1"]
