"""Tests for Accounting API endpoints."""
import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.accounting.factories import (
    AccountFactory,
    JournalEntryFactory,
    JournalFactory,
)
from modules.accounting.models import Account, Journal, JournalEntry


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


# ─── Chart of Accounts ────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAccountAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/accounting/accounts/")
        assert response.status_code == 401

    def test_list_returns_company_accounts(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        AccountFactory(company=company, code="1000", name="Cash")
        AccountFactory(company=company, code="2000", name="Payables")
        auth(api_client, user)

        response = api_client.get("/api/v1/accounting/accounts/")
        assert response.status_code == 200
        names = [a["name"] for a in response.json()]
        assert "Cash" in names
        assert "Payables" in names

    def test_accounts_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        AccountFactory(company=c1, code="1000", name="C1 Cash")
        AccountFactory(company=c2, code="1000", name="C2 Cash")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/accounting/accounts/")
        names = [a["name"] for a in response.json()]
        assert "C1 Cash" in names
        assert "C2 Cash" not in names

    def test_create_account(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/accounting/accounts/",
            {
                "code": "3000",
                "name": "Revenue",
                "account_type": Account.AccountType.REVENUE,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Revenue"

    def test_filter_by_account_type(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        AccountFactory(company=company, code="1000", name="Cash", account_type=Account.AccountType.ASSET)
        AccountFactory(company=company, code="4000", name="Revenue", account_type=Account.AccountType.REVENUE)
        auth(api_client, user)

        response = api_client.get("/api/v1/accounting/accounts/?account_type=asset")
        names = [a["name"] for a in response.json()]
        assert "Cash" in names
        assert "Revenue" not in names

    def test_filter_by_is_active(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        AccountFactory(company=company, code="1000", name="Active Acct", is_active=True)
        AccountFactory(company=company, code="9999", name="Inactive Acct", is_active=False)
        auth(api_client, user)

        response = api_client.get("/api/v1/accounting/accounts/?is_active=true")
        names = [a["name"] for a in response.json()]
        assert "Active Acct" in names
        assert "Inactive Acct" not in names


# ─── Journals ─────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestJournalAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/accounting/journals/")
        assert response.status_code == 401

    def test_list_returns_company_journals(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        JournalFactory(company=company, name="Sales Journal", code="SJ")
        JournalFactory(company=company, name="Purchase Journal", code="PJ")
        auth(api_client, user)

        response = api_client.get("/api/v1/accounting/journals/")
        assert response.status_code == 200
        names = [j["name"] for j in response.json()]
        assert "Sales Journal" in names
        assert "Purchase Journal" in names

    def test_journals_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        JournalFactory(company=c1, name="C1 Journal", code="J1")
        JournalFactory(company=c2, name="C2 Journal", code="J1")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/accounting/journals/")
        names = [j["name"] for j in response.json()]
        assert "C1 Journal" in names
        assert "C2 Journal" not in names

    def test_create_journal(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/accounting/journals/",
            {
                "name": "Cash Journal",
                "code": "CJ",
                "journal_type": Journal.JournalType.CASH,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Cash Journal"


# ─── Journal Entries ──────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestJournalEntryAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/accounting/entries/")
        assert response.status_code == 401

    def test_list_returns_company_entries(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        JournalEntryFactory(company=company, reference="JE-001")
        JournalEntryFactory(company=company, reference="JE-002")
        auth(api_client, user)

        response = api_client.get("/api/v1/accounting/entries/")
        assert response.status_code == 200
        refs = [e["reference"] for e in response.json()]
        assert "JE-001" in refs
        assert "JE-002" in refs

    def test_entries_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        JournalEntryFactory(company=c1, reference="C1-JE")
        JournalEntryFactory(company=c2, reference="C2-JE")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/accounting/entries/")
        refs = [e["reference"] for e in response.json()]
        assert "C1-JE" in refs
        assert "C2-JE" not in refs

    def test_create_entry(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        journal = JournalFactory(company=company, code="GJ")
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/accounting/entries/",
            {
                "journal": journal.pk,
                "reference": "JE-NEW-001",
                "status": JournalEntry.Status.DRAFT,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["reference"] == "JE-NEW-001"

    def test_filter_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        JournalEntryFactory(company=company, reference="DRAFT-JE", status=JournalEntry.Status.DRAFT)
        JournalEntryFactory(company=company, reference="POSTED-JE", status=JournalEntry.Status.POSTED)
        auth(api_client, user)

        response = api_client.get("/api/v1/accounting/entries/?status=draft")
        refs = [e["reference"] for e in response.json()]
        assert "DRAFT-JE" in refs
        assert "POSTED-JE" not in refs

    def test_filter_by_journal(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        j1 = JournalFactory(company=company, code="J1")
        j2 = JournalFactory(company=company, code="J2")
        JournalEntryFactory(company=company, journal=j1, reference="J1-JE")
        JournalEntryFactory(company=company, journal=j2, reference="J2-JE")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/accounting/entries/?journal={j1.pk}")
        refs = [e["reference"] for e in response.json()]
        assert "J1-JE" in refs
        assert "J2-JE" not in refs
