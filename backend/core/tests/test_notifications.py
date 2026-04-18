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

    def test_resaving_already_posted_invoice_does_not_spam(self):
        """REVIEW C-4: only the draft→posted transition should notify."""
        from modules.invoicing.models import Invoice

        company = CompanyFactory()
        admin = UserFactory(company=company, is_admin=True)
        invoice = Invoice.objects.create(
            company=company,
            invoice_number="INV-C4",
            customer_name="Acme",
            status="posted",
            total_amount=Decimal("100.00"),
            subtotal=Decimal("100.00"),
        )
        baseline = Notification.objects.filter(recipient=admin).count()

        # Every subsequent save must NOT generate another notification.
        for _ in range(3):
            invoice.subtotal = invoice.subtotal + Decimal("1.00")
            invoice.save()

        after = Notification.objects.filter(recipient=admin).count()
        assert after == baseline, (
            f"Invoice re-save must not spam admins — got {after - baseline} extra"
        )

    def test_draft_to_posted_transition_notifies(self):
        """The first draft→posted transition should still notify."""
        from modules.invoicing.models import Invoice

        company = CompanyFactory()
        admin = UserFactory(company=company, is_admin=True)
        invoice = Invoice.objects.create(
            company=company,
            invoice_number="INV-C4B",
            customer_name="Acme",
            status="draft",
            total_amount=Decimal("100.00"),
            subtotal=Decimal("100.00"),
        )
        before = Notification.objects.filter(recipient=admin).count()
        invoice.status = "posted"
        invoice.save()
        after = Notification.objects.filter(recipient=admin).count()
        assert after == before + 1

    def test_notify_many_admins_uses_single_query(self):
        """REVIEW C-7: notifying N admins should be 1 bulk INSERT, not N inserts."""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        from modules.helpdesk.models import Ticket, TicketCategory

        company = CompanyFactory()
        for _ in range(5):
            UserFactory(company=company, is_admin=True)
        category = TicketCategory.objects.create(company=company, name="General")

        with CaptureQueriesContext(connection) as ctx:
            Ticket.objects.create(
                company=company,
                ticket_number="TKT-BULK",
                title="Bulk test",
                category=category,
                priority="high",
                status="new",
            )

        notification_inserts = [
            q for q in ctx.captured_queries
            if "INSERT INTO" in q["sql"] and "core_notification" in q["sql"]
        ]
        assert len(notification_inserts) == 1, (
            f"Expected 1 bulk INSERT for 5 admins, got {len(notification_inserts)}"
        )

    def test_ticket_update_does_not_create_notification(self):
        """REVIEW C-9: edits to an existing ticket should not spam admins."""
        from modules.helpdesk.models import Ticket, TicketCategory

        company = CompanyFactory()
        admin = UserFactory(company=company, is_admin=True)
        category = TicketCategory.objects.create(company=company, name="General")
        ticket = Ticket.objects.create(
            company=company,
            ticket_number="TKT-C9",
            title="Printer",
            category=category,
            priority="high",
            status="new",
        )
        baseline = Notification.objects.filter(recipient=admin).count()

        ticket.title = "Printer (updated)"
        ticket.save()
        ticket.priority = "urgent"
        ticket.save()

        after = Notification.objects.filter(recipient=admin).count()
        assert after == baseline, (
            f"Ticket update must not spam admins — got {after - baseline} extra"
        )
