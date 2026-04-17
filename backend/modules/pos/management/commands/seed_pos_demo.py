from decimal import Decimal

from django.contrib.auth import get_user_model

from core.management.commands._seed_helpers import SeedCommandBase
from modules.pos.models import POSOrder, POSSession


class Command(SeedCommandBase):
    help = "Seed a demo POS session + order for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            POSOrder.objects.filter(company=company).delete()
            POSSession.objects.filter(company=company).delete()

        User = get_user_model()
        user = User.objects.filter(profile__company=company).first()
        if user is None:
            # No user for this company; skip but don't fail.
            return 0

        session, _ = POSSession.objects.get_or_create(
            company=company,
            station="Demo Station",
            status="open",
            defaults={
                "cash_on_open": Decimal("100.00"),
                "opened_by": user,
            },
        )
        POSOrder.objects.get_or_create(
            company=company,
            session=session,
            order_number="DEMO-POS-1",
            defaults={
                "subtotal": Decimal("20.00"),
                "tax_amount": Decimal("2.00"),
                "total": Decimal("22.00"),
                "status": "paid",
            },
        )
        return 2
