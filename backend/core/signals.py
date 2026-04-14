from django.db.models.signals import post_delete, post_save
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
