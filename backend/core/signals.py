from django.db.models.signals import post_delete, post_init, post_save
from django.dispatch import receiver

from core.models import AuditLog, Company, IndustryConfigTemplate, ModuleConfig, TenantModel


# REVIEW I-7: models/events to exclude from AuditLog to keep the 100-row
# UI timeline focused on user actions rather than framework plumbing.
_AUDIT_LOG_EXCLUDED_MODELS = frozenset({
    "AuditLog",         # recursion guard
    "Notification",     # high-frequency, not user-initiated
    "Sequence",         # sequence-counter bumps on every numbered save
    "IndustryConfigTemplate",  # seeded at deploy; not user actions
    "ModuleRegistry",   # same
    "ViewDefinition",   # same
})


@receiver(post_save)
def create_audit_log(sender, instance, created, **kwargs):
    """Log create/update actions on TenantModel subclasses.

    REVIEW I-7: skip raw fixture loads (``kwargs["raw"]``) and a blocklist
    of framework-plumbing models so the audit timeline shows real user
    actions — not sequence counters, notifications, or seed noise.
    """
    if not isinstance(instance, TenantModel):
        return

    if kwargs.get("raw"):
        # loaddata / fixture replay — do not audit.
        return

    if sender.__name__ in _AUDIT_LOG_EXCLUDED_MODELS:
        return

    company = getattr(instance, "company", None)

    AuditLog.objects.create(
        company=company,
        user=None,
        model_name=sender.__name__,
        model_id=str(instance.pk),
        action="create" if created else "update",
        new_values={"saved": True},
    )


# ──────────────────────────────────────────────────────────────────────────────
# Config Cache Invalidation
# ──────────────────────────────────────────────────────────────────────────────


@receiver(post_save, sender=IndustryConfigTemplate)
def invalidate_on_industry_template_change(sender, instance, **kwargs):
    """Invalidate cached config for all companies in this industry."""
    from core.services.config_service import invalidate_industry_config

    invalidate_industry_config(instance.industry)


@receiver(post_save, sender=Company)
def invalidate_on_company_config_change(sender, instance, **kwargs):
    """Invalidate cached config for this company when config_json changes."""
    from core.services.config_service import invalidate_company_config

    invalidate_company_config(instance.id)


@receiver(post_save, sender=ModuleConfig)
@receiver(post_delete, sender=ModuleConfig)
def invalidate_on_module_config_change(sender, instance, **kwargs):
    """Invalidate cached config for the company when any ModuleConfig is saved/deleted."""
    from core.services.config_service import invalidate_company_config

    invalidate_company_config(instance.company_id)


# ──────────────────────────────────────────────────────────────────────────────
# Slice 19 — Notifications for key business events
# ──────────────────────────────────────────────────────────────────────────────


def _notify_company_admins(company, title, message, notification_type="info",
                            related_model="", related_id=None, action_url=""):
    """Create a Notification for every company admin in this company.

    REVIEW C-7: uses a single ``bulk_create`` so that 1 ticket save = 1 + 1
    INSERT (ticket + bulk admin notifications) instead of 1 + N. This keeps
    the signal chain O(1) queries regardless of admin count. Async offload
    via Celery is still a future improvement but not required for MVP.
    """
    from core.models import Notification, UserProfile

    admin_user_ids = list(
        UserProfile.objects.filter(
            company=company, is_company_admin=True
        ).values_list("user_id", flat=True)
    )
    if not admin_user_ids:
        return

    Notification.objects.bulk_create([
        Notification(
            recipient_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_model=related_model,
            related_id=related_id,
            action_url=action_url,
        )
        for user_id in admin_user_ids
    ])


# REVIEW S-3: registry-driven notification signals. Each rule declares the
# model path, an optional pre-save field to watch (for transition
# detection), a ``should_notify`` predicate, and a ``build`` function that
# returns the Notification kwargs. _register_notification_signals walks
# the list once and wires up post_init (if watch_field) + post_save for
# each rule.
NOTIFICATION_RULES = [
    {
        "module_path": "modules.helpdesk.models",
        "class_name": "Ticket",
        "watch_field": None,
        "should_notify": lambda inst, created, prev: created,
        "build": lambda inst: {
            "title": f"New ticket: {inst.title}",
            "message": f"Priority {inst.priority} — {inst.ticket_number}",
            "notification_type": "info",
            "related_model": "Ticket",
            "related_id": inst.pk,
            "action_url": f"/helpdesk/tickets/{inst.pk}/edit",
        },
    },
    {
        "module_path": "modules.invoicing.models",
        "class_name": "Invoice",
        # REVIEW C-4: watch `status` so post_save can detect the
        # draft→posted transition rather than firing on every save.
        "watch_field": "status",
        "should_notify": lambda inst, created, prev: (
            inst.status == "posted" and (created or prev != "posted")
        ),
        "build": lambda inst: {
            "title": f"Invoice posted: {inst.invoice_number}",
            "message": f"{inst.customer_name} — ${inst.total_amount}",
            "notification_type": "success",
            "related_model": "Invoice",
            "related_id": inst.pk,
            "action_url": f"/invoicing/invoices/{inst.pk}/edit",
        },
    },
]


def _register_notification_signals():
    """Wire up post_save (and post_init for transition rules) for every rule
    in ``NOTIFICATION_RULES``. Called from apps.ready().

    REVIEW S-3: collapses two near-identical try/except blocks into one
    registry-driven loop.
    """
    from importlib import import_module

    for rule in NOTIFICATION_RULES:
        try:
            module = import_module(rule["module_path"])
            model_cls = getattr(module, rule["class_name"])
        except (ImportError, AttributeError):
            # Module not installed → skip this rule.
            continue

        # Each rule closes over its own model + watch_field; we use defaults
        # in the inner functions to capture the current loop value.
        watch_field = rule["watch_field"]
        should_notify = rule["should_notify"]
        build = rule["build"]

        if watch_field:
            @receiver(post_init, sender=model_cls, weak=False)
            def _cache_prev(sender, instance, _field=watch_field, **kwargs):
                setattr(instance, f"_prev_{_field}", getattr(instance, _field))

        @receiver(post_save, sender=model_cls, weak=False)
        def _on_save(
            sender, instance, created,
            _watch=watch_field, _should=should_notify, _build=build,
            **kwargs,
        ):
            prev = getattr(instance, f"_prev_{_watch}", None) if _watch else None
            # Refresh cache immediately so subsequent saves on the same
            # Python instance see the new "prev" state.
            if _watch:
                setattr(instance, f"_prev_{_watch}", getattr(instance, _watch))
            if not _should(instance, created, prev):
                return
            kwargs_out = _build(instance)
            _notify_company_admins(instance.company, **kwargs_out)
