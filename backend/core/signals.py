from django.db.models.signals import post_delete, post_init, post_save
from django.dispatch import receiver

from core.models import AuditLog, Company, IndustryConfigTemplate, ModuleConfig, TenantModel


@receiver(post_save)
def create_audit_log(sender, instance, created, **kwargs):
    """Log create/update actions on TenantModel subclasses."""
    if not isinstance(instance, TenantModel):
        return

    # Don't log AuditLog itself to avoid recursion
    if sender is AuditLog:
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
    """Create a Notification for every company admin in this company."""
    from core.models import Notification, UserProfile

    admins = UserProfile.objects.filter(
        company=company, is_company_admin=True
    ).select_related("user")
    for profile in admins:
        Notification.objects.create(
            recipient=profile.user,
            title=title,
            message=message,
            notification_type=notification_type,
            related_model=related_model,
            related_id=related_id,
            action_url=action_url,
        )


def _register_notification_signals():
    """Wire up post_save handlers on business models. Called from apps.ready()."""
    try:
        from modules.helpdesk.models import Ticket

        @receiver(post_save, sender=Ticket, weak=False)
        def on_ticket_saved(sender, instance, created, **kwargs):
            if not created:
                return
            _notify_company_admins(
                instance.company,
                title=f"New ticket: {instance.title}",
                message=f"Priority {instance.priority} — {instance.ticket_number}",
                notification_type="info",
                related_model="Ticket",
                related_id=instance.pk,
                action_url=f"/helpdesk/tickets/{instance.pk}/edit",
            )
    except Exception:
        pass

    try:
        from modules.invoicing.models import Invoice

        # REVIEW C-4: only notify on the draft→posted transition, not on every
        # save of an already-posted invoice. We track the pre-save status on
        # each instance via post_init; post_save compares against it.

        @receiver(post_init, sender=Invoice, weak=False)
        def cache_invoice_status(sender, instance, **kwargs):
            instance._prev_status = instance.status

        @receiver(post_save, sender=Invoice, weak=False)
        def on_invoice_saved(sender, instance, created, **kwargs):
            prev = getattr(instance, "_prev_status", None)
            is_transition = (
                instance.status == "posted"
                and (created or prev != "posted")
            )
            # Refresh the cached status so subsequent saves in the same
            # Python object compare against the new value.
            instance._prev_status = instance.status

            if not is_transition:
                return
            _notify_company_admins(
                instance.company,
                title=f"Invoice posted: {instance.invoice_number}",
                message=f"{instance.customer_name} — ${instance.total_amount}",
                notification_type="success",
                related_model="Invoice",
                related_id=instance.pk,
                action_url=f"/invoicing/invoices/{instance.pk}/edit",
            )
    except Exception:
        pass
