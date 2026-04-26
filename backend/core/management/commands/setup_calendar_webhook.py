"""Provision or update a company's calendar webhook config (Slice 22).

Usage::

    python manage.py setup_calendar_webhook \
        --company novapay \
        --peer-url https://crm.novapay.com/api/v1/webhooks/calendar/novapay/ \
        --shared-secret <32-byte hex> \
        [--enable | --disable]

The hex shared secret should be the **same value** entered on both sides
(ERP + CRM) — it's the HMAC key used to sign and verify both directions.
Generate once with::

    python -c "import secrets; print(secrets.token_hex(32))"

See docs/CALENDAR-SYNC-WEBHOOKS.md §Configuration.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from core.models import Company, CompanyWebhookConfig


class Command(BaseCommand):
    help = "Create or update a company's calendar webhook config."

    def add_arguments(self, parser):
        parser.add_argument(
            "--company", required=True,
            help="Company slug (e.g. novapay).",
        )
        parser.add_argument(
            "--peer-url", required=True,
            help="Where outbound webhooks should be POSTed.",
        )
        parser.add_argument(
            "--shared-secret", required=True,
            help="32+ byte hex shared HMAC key (same value on both sides).",
        )
        parser.add_argument("--enable", action="store_true",
                            help="Set enabled=True on this config.")
        parser.add_argument("--disable", action="store_true",
                            help="Set enabled=False on this config.")

    def handle(self, *args, **options):
        slug = options["company"]
        peer_url = options["peer_url"]
        secret = options["shared_secret"]
        enable = options["enable"]
        disable = options["disable"]

        if enable and disable:
            raise CommandError("--enable and --disable are mutually exclusive.")

        try:
            company = Company.objects.get(slug=slug)
        except Company.DoesNotExist:
            raise CommandError(f"No company with slug {slug!r}.")

        cfg, created = CompanyWebhookConfig.objects.update_or_create(
            company=company,
            defaults={
                "peer_url": peer_url,
                "shared_secret": secret,
            },
        )
        # `enabled` is preserved on update unless an explicit flag is passed.
        if enable:
            cfg.enabled = True
            cfg.save(update_fields=["enabled"])
        elif disable:
            cfg.enabled = False
            cfg.save(update_fields=["enabled"])

        verb = "Created" if created else "Updated"
        state = "enabled" if cfg.enabled else "disabled"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} webhook config for {slug} → {peer_url} ({state})."
            )
        )
