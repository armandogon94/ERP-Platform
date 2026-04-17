from core.management.commands._seed_helpers import SeedCommandBase
from modules.accounting.models import Account, Journal, JournalEntry


class Command(SeedCommandBase):
    help = "Seed demo chart-of-accounts + journal + one entry for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            JournalEntry.objects.filter(company=company).delete()
            Journal.objects.filter(company=company).delete()
            Account.objects.filter(company=company).delete()

        accounts = [
            ("1000", "Cash", "asset"),
            ("1200", "Accounts Receivable", "asset"),
            ("2000", "Accounts Payable", "liability"),
            ("3000", "Equity", "equity"),
            ("4000", "Revenue", "revenue"),
            ("5000", "Expenses", "expense"),
        ]
        for code, name, acct_type in accounts:
            Account.objects.get_or_create(
                company=company,
                code=code,
                defaults={"name": name, "account_type": acct_type},
            )
        journal, _ = Journal.objects.get_or_create(
            company=company,
            code="GJ",
            defaults={"name": "General Journal", "journal_type": "general"},
        )
        JournalEntry.objects.get_or_create(
            company=company,
            reference="DEMO-JE-1",
            defaults={"journal": journal, "status": "draft"},
        )
        return len(accounts) + 2
