from core.management.commands._seed_helpers import SeedCommandBase
from modules.helpdesk.models import (
    KnowledgeArticle,
    SLAConfig,
    Ticket,
    TicketCategory,
)


class Command(SeedCommandBase):
    help = "Seed demo categories + SLA configs + tickets + KB article for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            Ticket.objects.filter(company=company).delete()
            SLAConfig.objects.filter(company=company).delete()
            KnowledgeArticle.objects.filter(company=company).delete()
            TicketCategory.objects.filter(company=company).delete()

        billing, _ = TicketCategory.objects.get_or_create(
            company=company,
            name="Billing",
            defaults={"sla_hours": 24},
        )
        tech, _ = TicketCategory.objects.get_or_create(
            company=company,
            name="Technical",
            defaults={"sla_hours": 4},
        )
        SLAConfig.objects.get_or_create(
            company=company,
            category=billing,
            priority="normal",
            defaults={"response_hours": 4, "resolution_hours": 24},
        )
        SLAConfig.objects.get_or_create(
            company=company,
            category=tech,
            priority="high",
            defaults={"response_hours": 1, "resolution_hours": 4},
        )
        ticket_specs = [
            ("Demo issue: login failure", tech, "high", "new"),
            ("Demo issue: billing question", billing, "normal", "in_progress"),
        ]
        for title, cat, priority, status in ticket_specs:
            Ticket.objects.get_or_create(
                company=company,
                title=title,
                defaults={
                    "category": cat,
                    "priority": priority,
                    "status": status,
                },
            )
        KnowledgeArticle.objects.get_or_create(
            company=company,
            slug="demo-reset-password",
            defaults={
                "title": "How to reset your password",
                "body": "Step 1... Step 2...",
                "category": tech,
                "published": True,
            },
        )
        return 2 + 2 + len(ticket_specs) + 1
