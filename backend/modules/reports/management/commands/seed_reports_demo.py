from core.management.commands._seed_helpers import SeedCommandBase
from modules.reports.models import PivotDefinition, ReportTemplate


class Command(SeedCommandBase):
    help = "Seed demo ReportTemplate + PivotDefinition rows for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            PivotDefinition.objects.filter(company=company).delete()
            ReportTemplate.objects.filter(company=company).delete()

        templates = [
            (
                "Revenue by Status",
                "invoicing.Invoice",
                ["status"],
                ["total_amount"],
            ),
            (
                "Tickets by Priority",
                "helpdesk.Ticket",
                ["priority"],
                ["id"],
            ),
        ]
        for name, model, group_by, measures in templates:
            ReportTemplate.objects.get_or_create(
                company=company,
                name=name,
                defaults={
                    "model_name": model,
                    "default_group_by": group_by,
                    "default_measures": measures,
                },
            )

        PivotDefinition.objects.get_or_create(
            company=company,
            name="Demo Invoice Pivot",
            defaults={
                "model_name": "invoicing.Invoice",
                "rows": ["status"],
                "measure": "total_amount",
                "aggregator": "sum",
            },
        )
        return len(templates) + 1
