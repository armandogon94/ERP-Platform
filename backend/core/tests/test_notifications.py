"""Tests for the Notifications REST API and signal handlers (Slice 19)."""

from decimal import Decimal

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from core.models import Notification


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestNotificationsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/core/notifications/")
        assert response.status_code == 401

    def test_list_returns_only_recipient_notifications(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        other = UserFactory(company=company)
        Notification.objects.create(
            recipient=user, title="Yours", notification_type="info"
        )
        Notification.objects.create(
            recipient=other, title="Not yours", notification_type="info"
        )
        auth(api_client, user)

        response = api_client.get("/api/v1/core/notifications/")
        assert response.status_code == 200
        titles = [n["title"] for n in response.json()]
        assert "Yours" in titles
        assert "Not yours" not in titles

    def test_mark_read_endpoint(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        n = Notification.objects.create(
            recipient=user, title="Hi", notification_type="info"
        )
        auth(api_client, user)

        response = api_client.post(f"/api/v1/core/notifications/{n.id}/mark_read/")
        assert response.status_code == 200
        n.refresh_from_db()
        assert n.is_read is True

    def test_unread_count_endpoint(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        Notification.objects.create(
            recipient=user, title="A", notification_type="info", is_read=False
        )
        Notification.objects.create(
            recipient=user, title="B", notification_type="info", is_read=False
        )
        Notification.objects.create(
            recipient=user, title="C", notification_type="info", is_read=True
        )
        auth(api_client, user)

        response = api_client.get("/api/v1/core/notifications/unread_count/")
        assert response.status_code == 200
        assert response.json() == {"count": 2}


@pytest.mark.django_db
class TestNotificationSignals:
    def test_new_helpdesk_ticket_creates_notification(self):
        from modules.helpdesk.models import Ticket, TicketCategory

        company = CompanyFactory()
        admin = UserFactory(company=company, is_admin=True)
        category = TicketCategory.objects.create(company=company, name="General")
        before = Notification.objects.filter(recipient=admin).count()
        Ticket.objects.create(
            company=company,
            ticket_number="TKT-1",
            title="Printer broken",
            category=category,
            priority="high",
            status="new",
        )
        after = Notification.objects.filter(recipient=admin).count()
        assert after == before + 1
        n = Notification.objects.filter(recipient=admin).latest("created_at")
        assert "Printer broken" in n.title or "Printer broken" in n.message

    def test_posted_invoice_creates_notification(self):
        from modules.invoicing.models import Invoice

        company = CompanyFactory()
        admin = UserFactory(company=company, is_admin=True)
        before = Notification.objects.filter(recipient=admin).count()
        Invoice.objects.create(
            company=company,
            invoice_number="INV-1",
            customer_name="Acme",
            status="posted",
            total_amount=Decimal("500.00"),
            subtotal=Decimal("500.00"),
        )
        after = Notification.objects.filter(recipient=admin).count()
        assert after >= before + 1
