"""Tests for the Audit Log REST API (Slice 19)."""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from core.models import AuditLog


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestAuditLogAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/core/audit-logs/")
        assert response.status_code == 401

    def test_list_returns_company_scoped_entries(self, api_client):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        user_a = UserFactory(company=company_a)
        AuditLog.objects.create(
            company=company_a, user=user_a, model_name="Invoice",
            model_id=1, action="create", new_values={"number": "INV-A"},
        )
        AuditLog.objects.create(
            company=company_b, user=None, model_name="Invoice",
            model_id=99, action="create", new_values={"number": "INV-B"},
        )
        auth(api_client, user_a)

        response = api_client.get("/api/v1/core/audit-logs/")
        assert response.status_code == 200
        body = response.json()
        ids = [e["model_id"] for e in body]
        assert 1 in ids
        assert 99 not in ids

    def test_notifications_do_not_pollute_audit_timeline(self, api_client):
        """REVIEW I-7: Notification creates shouldn't create AuditLog rows."""
        from core.models import Notification

        company = CompanyFactory()
        user = UserFactory(company=company)
        before = AuditLog.objects.filter(company=company).count()
        Notification.objects.create(
            recipient=user, title="Hi", notification_type="info"
        )
        after = AuditLog.objects.filter(company=company).count()
        assert after == before, (
            "Notification saves must be excluded from the audit timeline "
            f"(got {after - before} new rows)"
        )

    def test_list_ordered_by_most_recent_first(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        AuditLog.objects.create(
            company=company, user=user, model_name="Invoice",
            model_id=1, action="create", new_values={},
        )
        AuditLog.objects.create(
            company=company, user=user, model_name="Invoice",
            model_id=2, action="update", new_values={},
        )
        auth(api_client, user)
        response = api_client.get("/api/v1/core/audit-logs/")
        body = response.json()
        # Most recent first
        assert body[0]["model_id"] == 2
        assert body[1]["model_id"] == 1
