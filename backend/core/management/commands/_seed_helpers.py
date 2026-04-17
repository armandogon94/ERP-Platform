"""Shared helpers for `seed_*_demo` management commands (Slice 17)."""

from django.core.management.base import BaseCommand, CommandError

from core.models import Company


class SeedCommandBase(BaseCommand):
    """Base class for `seed_<module>_demo` commands.

    Subclasses implement `seed(company, reset: bool)` — idempotent.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--company",
            required=True,
            help="Company slug to seed (e.g. 'novapay', 'tablesync')",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing seed rows before creating fresh ones",
        )

    def handle(self, *args, **options):
        slug = options["company"]
        reset = options["reset"]
        try:
            company = Company.objects.get(slug=slug)
        except Company.DoesNotExist as exc:
            raise CommandError(f"Company '{slug}' not found") from exc

        created = self.seed(company, reset=reset)
        self.stdout.write(
            self.style.SUCCESS(
                f"{self.__module__}: {created} record(s) seeded for {slug}."
            )
        )

    def seed(self, company: Company, *, reset: bool) -> int:
        raise NotImplementedError
