from decimal import Decimal

from core.management.commands._seed_helpers import SeedCommandBase
from modules.sales.models import SalesOrder, SalesQuotation


class Command(SeedCommandBase):
    help = "Seed demo sales quotations + orders for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            SalesOrder.objects.filter(company=company).delete()
            SalesQuotation.objects.filter(company=company).delete()

        quote_specs = [
            ("DEMO-Q-1", "Acme Corp", "sent", Decimal("1200.00")),
            ("DEMO-Q-2", "Globex Inc", "draft", Decimal("450.00")),
        ]
        for number, cust, status, total in quote_specs:
            SalesQuotation.objects.get_or_create(
                company=company,
                quotation_number=number,
                defaults={
                    "customer_name": cust,
                    "status": status,
                    "total_amount": total,
                },
            )

        order_specs = [
            ("DEMO-SO-1", "Acme Corp", "confirmed", Decimal("1200.00")),
            ("DEMO-SO-2", "Globex Inc", "delivered", Decimal("450.00")),
        ]
        for number, cust, status, total in order_specs:
            SalesOrder.objects.get_or_create(
                company=company,
                order_number=number,
                defaults={
                    "customer_name": cust,
                    "status": status,
                    "total_amount": total,
                },
            )
        return len(quote_specs) + len(order_specs)
