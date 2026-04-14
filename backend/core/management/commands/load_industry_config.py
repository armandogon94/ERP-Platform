"""Management command: load_industry_config

Reads YAML files from core/industry_configs/ and upserts IndustryConfigTemplate rows.

Usage:
    python manage.py load_industry_config              # load all 10 industries
    python manage.py load_industry_config --industry dental
    python manage.py load_industry_config --dry-run   # validate without writing
"""

import os
from pathlib import Path

import yaml
from django.core.management.base import BaseCommand, CommandError

from core.models import Industry, IndustryConfigTemplate

CONFIGS_DIR = Path(__file__).resolve().parent.parent.parent / "industry_configs"

VALID_INDUSTRIES = {choice[0] for choice in Industry.choices}


class Command(BaseCommand):
    help = "Load industry configuration YAML files into IndustryConfigTemplate records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--industry",
            type=str,
            default=None,
            help="Load a single industry by slug (e.g. dental). Default: load all.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Validate YAML files and print what would be loaded without writing to DB.",
        )

    def handle(self, *args, **options):
        industry_filter = options.get("industry")
        dry_run = options.get("dry_run")

        if industry_filter and industry_filter not in VALID_INDUSTRIES:
            raise CommandError(
                f"Unknown industry: '{industry_filter}'. "
                f"Valid choices: {sorted(VALID_INDUSTRIES)}"
            )

        yaml_files = self._collect_yaml_files(industry_filter)

        if not yaml_files:
            raise CommandError(
                f"No YAML files found in {CONFIGS_DIR}"
                + (f" for industry '{industry_filter}'" if industry_filter else "")
            )

        created = 0
        updated = 0

        for yaml_path in sorted(yaml_files):
            config_data = self._load_and_validate(yaml_path)
            industry_slug = config_data["industry"]

            if dry_run:
                if options["verbosity"] >= 1:
                    self.stdout.write(f"  [dry-run] Would upsert: {industry_slug}")
                continue

            obj, was_created = IndustryConfigTemplate.objects.get_or_create(
                industry=industry_slug,
                defaults={"config": config_data},
            )
            if not was_created:
                obj.config = config_data
                obj.save(update_fields=["config", "updated_at"])
                updated += 1
            else:
                created += 1

            if options["verbosity"] >= 2:
                action = "created" if was_created else "updated"
                self.stdout.write(f"  {action}: {industry_slug}")

        if not dry_run and options["verbosity"] >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f"load_industry_config: {created} created, {updated} updated."
                )
            )

    def _collect_yaml_files(self, industry_filter):
        if not CONFIGS_DIR.exists():
            raise CommandError(f"Config directory not found: {CONFIGS_DIR}")

        if industry_filter:
            target = CONFIGS_DIR / f"{industry_filter}.yaml"
            if not target.exists():
                raise CommandError(f"Config file not found: {target}")
            return [target]

        return list(CONFIGS_DIR.glob("*.yaml"))

    def _load_and_validate(self, yaml_path: Path) -> dict:
        try:
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise CommandError(f"Invalid YAML in {yaml_path}: {e}")

        if not isinstance(data, dict):
            raise CommandError(f"Expected a YAML mapping in {yaml_path}, got {type(data)}")

        if "industry" not in data:
            raise CommandError(f"Missing required 'industry' key in {yaml_path}")

        if data["industry"] not in VALID_INDUSTRIES:
            raise CommandError(
                f"Unknown industry '{data['industry']}' in {yaml_path}. "
                f"Valid choices: {sorted(VALID_INDUSTRIES)}"
            )

        return data
