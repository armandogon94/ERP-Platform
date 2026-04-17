from decimal import Decimal

from core.management.commands._seed_helpers import SeedCommandBase
from modules.invoicing.models import Invoice


class Command(SeedCommandBase):
    help = "Seed demo invoices for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            Invoice.objects.filter(company=company).delete()

        specs = [
            ("DEMO-INV-1", "Acme Corp", "paid", Decimal("1500.00")),
            ("DEMO-INV-2", "Globex Inc", "posted", Decimal("2200.00")),
            ("DEMO-INV-3", "Widget LLC", "draft", Decimal("850.00")),
        ]
        for number, cust, status, total in specs:
            Invoice.objects.get_or_create(
                company=company,
                invoice_number=number,
                defaults={
                    "customer_name": cust,
                    "status": status,
                    "total_amount": total,
                    "subtotal": total,
                },
            )
        return len(specs)
