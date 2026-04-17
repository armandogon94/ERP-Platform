"""Meta-command: seed demo data across the module subset for a company's industry."""

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from core.industry_modules import modules_for_industry
from core.models import Company


# Map module slug (from industry_modules) → management command name.
# Slugs that don't map to a real seeder (e.g. "partners") are skipped.
MODULE_COMMANDS: dict[str, str] = {
    "hr": "seed_hr_demo",
    "calendar": "seed_calendar_demo",
    "inventory": "seed_inventory_demo",
    "sales": "seed_sales_demo",
    "purchasing": "seed_purchasing_demo",
    "invoicing": "seed_invoicing_demo",
    "accounting": "seed_accounting_demo",
    "fleet": "seed_fleet_demo",
    "projects": "seed_projects_demo",
    "manufacturing": "seed_manufacturing_demo",
    "pos": "seed_pos_demo",
    "helpdesk": "seed_helpdesk_demo",
    "reports": "seed_reports_demo",
}


class Command(BaseCommand):
    help = (
        "Seed demo data for a company using the module subset defined for its "
        "industry (see core.industry_modules)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--company", required=True)
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        slug = options["company"]
        reset = options["reset"]
        try:
            company = Company.objects.get(slug=slug)
        except Company.DoesNotExist as exc:
            raise CommandError(f"Company '{slug}' not found") from exc

        modules = modules_for_industry(company.industry)
        for module_slug in modules:
            command = MODULE_COMMANDS.get(module_slug)
            if command is None:
                continue  # slugs like "partners" have no seeder yet
            self.stdout.write(
                f"  → running {command} for {slug} ({company.industry})"
            )
            extra = {"reset": reset} if reset else {}
            call_command(command, company=slug, stdout=self.stdout, **extra)

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_industry_demo: completed for {slug} ({company.industry})."
            )
        )
