"""Tests for Accounting module models: ChartOfAccounts, Journal, JournalEntry."""
import pytest
from decimal import Decimal

from core.factories import CompanyFactory
from modules.accounting.factories import (
    AccountFactory,
    JournalEntryFactory,
    JournalEntryLineFactory,
    JournalFactory,
)
from modules.accounting.models import Account, Journal, JournalEntry, JournalEntryLine


@pytest.mark.django_db
class TestAccountModel:
    def test_create_account(self):
        company = CompanyFactory()
        account = Account.objects.create(
            company=company,
            code="1000",
            name="Cash",
            account_type=Account.AccountType.ASSET,
        )
        assert account.pk is not None
        assert account.code == "1000"
        assert account.name == "Cash"

    def test_account_str_contains_code_and_name(self):
        account = AccountFactory(code="2000", name="Accounts Payable")
        assert "2000" in str(account)
        assert "Accounts Payable" in str(account)

    def test_account_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        AccountFactory(company=c1)
        AccountFactory(company=c2)
        assert Account.objects.filter(company=c1).count() == 1
        assert Account.objects.filter(company=c2).count() == 1

    def test_account_type_choices(self):
        account = AccountFactory(account_type=Account.AccountType.LIABILITY)
        assert account.account_type == Account.AccountType.LIABILITY

    def test_account_factory(self):
        account = AccountFactory()
        assert account.pk is not None
        assert account.code

    def test_account_soft_delete(self):
        account = AccountFactory()
        account.soft_delete()
        assert Account.objects.filter(pk=account.pk).count() == 0
        assert Account.all_objects.filter(pk=account.pk).count() == 1

    def test_account_is_active_default(self):
        account = AccountFactory()
        assert account.is_active is True

    def test_account_parent_hierarchy(self):
        company = CompanyFactory()
        parent = AccountFactory(company=company, code="1000", name="Assets")
        child = AccountFactory(company=company, code="1010", name="Cash", parent=parent)
        assert child.parent == parent


@pytest.mark.django_db
class TestJournalModel:
    def test_create_journal(self):
        company = CompanyFactory()
        journal = Journal.objects.create(
            company=company,
            name="General Journal",
            journal_type=Journal.JournalType.GENERAL,
            code="GJ",
        )
        assert journal.pk is not None
        assert journal.name == "General Journal"

    def test_journal_str_contains_name(self):
        journal = JournalFactory(name="Sales Journal")
        assert "Sales Journal" in str(journal)

    def test_journal_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        JournalFactory(company=c1)
        JournalFactory(company=c2)
        assert Journal.objects.filter(company=c1).count() == 1
        assert Journal.objects.filter(company=c2).count() == 1

    def test_journal_type_choices(self):
        journal = JournalFactory(journal_type=Journal.JournalType.PURCHASE)
        assert journal.journal_type == Journal.JournalType.PURCHASE

    def test_journal_factory(self):
        journal = JournalFactory()
        assert journal.pk is not None
        assert journal.code

    def test_journal_soft_delete(self):
        journal = JournalFactory()
        journal.soft_delete()
        assert Journal.objects.filter(pk=journal.pk).count() == 0
        assert Journal.all_objects.filter(pk=journal.pk).count() == 1


@pytest.mark.django_db
class TestJournalEntryModel:
    def test_create_journal_entry(self):
        company = CompanyFactory()
        journal = JournalFactory(company=company)
        entry = JournalEntry.objects.create(
            company=company,
            journal=journal,
            reference="JE-2026-001",
            status=JournalEntry.Status.DRAFT,
        )
        assert entry.pk is not None
        assert entry.reference == "JE-2026-001"

    def test_entry_str_contains_reference(self):
        entry = JournalEntryFactory(reference="JE-2026-042")
        assert "JE-2026-042" in str(entry)

    def test_entry_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        JournalEntryFactory(company=c1)
        JournalEntryFactory(company=c2)
        assert JournalEntry.objects.filter(company=c1).count() == 1
        assert JournalEntry.objects.filter(company=c2).count() == 1

    def test_entry_status_choices(self):
        entry = JournalEntryFactory(status=JournalEntry.Status.POSTED)
        assert entry.status == JournalEntry.Status.POSTED

    def test_entry_factory(self):
        entry = JournalEntryFactory()
        assert entry.pk is not None
        assert entry.journal is not None

    def test_entry_soft_delete(self):
        entry = JournalEntryFactory()
        entry.soft_delete()
        assert JournalEntry.objects.filter(pk=entry.pk).count() == 0
        assert JournalEntry.all_objects.filter(pk=entry.pk).count() == 1

    def test_entry_default_status_is_draft(self):
        entry = JournalEntryFactory()
        assert entry.status == JournalEntry.Status.DRAFT


@pytest.mark.django_db
class TestJournalEntryLineModel:
    def test_create_entry_line(self):
        company = CompanyFactory()
        entry = JournalEntryFactory(company=company)
        account = AccountFactory(company=company)
        line = JournalEntryLine.objects.create(
            company=company,
            journal_entry=entry,
            account=account,
            label="Cash receipt",
            debit=Decimal("500.00"),
            credit=Decimal("0.00"),
        )
        assert line.pk is not None
        assert line.debit == Decimal("500.00")

    def test_entry_line_str_contains_label(self):
        line = JournalEntryLineFactory(label="Revenue recognition")
        assert "Revenue recognition" in str(line)

    def test_entry_line_factory(self):
        line = JournalEntryLineFactory()
        assert line.pk is not None
        assert line.journal_entry is not None
        assert line.account is not None

    def test_entry_line_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        JournalEntryLineFactory(company=c1)
        JournalEntryLineFactory(company=c2)
        assert JournalEntryLine.objects.filter(company=c1).count() == 1
        assert JournalEntryLine.objects.filter(company=c2).count() == 1
