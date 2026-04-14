import factory
from decimal import Decimal

from core.factories import CompanyFactory
from modules.accounting.models import Account, Journal, JournalEntry, JournalEntryLine


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    code = factory.Sequence(lambda n: f"{1000 + n}")
    name = factory.Sequence(lambda n: f"Account {n}")
    account_type = Account.AccountType.ASSET
    parent = None
    description = ""
    is_active = True


class JournalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Journal
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Journal {n}")
    code = factory.Sequence(lambda n: f"J{n:02d}")
    journal_type = Journal.JournalType.GENERAL
    default_account = None


class JournalEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JournalEntry
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    journal = factory.SubFactory(JournalFactory, company=factory.SelfAttribute("..company"))
    reference = factory.Sequence(lambda n: f"JE-2026-{n:03d}")
    status = JournalEntry.Status.DRAFT


class JournalEntryLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JournalEntryLine
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    journal_entry = factory.SubFactory(
        JournalEntryFactory, company=factory.SelfAttribute("..company")
    )
    account = factory.SubFactory(AccountFactory, company=factory.SelfAttribute("..company"))
    label = factory.Sequence(lambda n: f"Entry line {n}")
    debit = Decimal("100.00")
    credit = Decimal("0.00")
