from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import AuditLog, TenantModel


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
