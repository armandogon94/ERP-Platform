from django.conf import settings
from django.db import models
from django.utils import timezone

from core.managers import SoftDeleteManager


class TenantModel(models.Model):
    """Abstract base class for all tenant-scoped models.

    Provides: company FK, timestamps, soft delete, and audit fields.
    All module models inherit from this.
    """

    company = models.ForeignKey(
        "core.Company",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])


class Industry(models.TextChoices):
    FINTECH = "fintech", "FinTech"
    HEALTHCARE = "healthcare", "Healthcare"
    INSURANCE = "insurance", "Insurance"
    REAL_ESTATE = "real_estate", "Real Estate"
    LOGISTICS = "logistics", "Logistics"
    DENTAL = "dental", "Dental Clinic"
    LEGAL = "legal", "Legal Firm"
    HOSPITALITY = "hospitality", "Hospitality/Restaurant"
    CONSTRUCTION = "construction", "Construction"
    EDUCATION = "education", "Education"


class Company(models.Model):
    """Tenant root. All data belongs to a Company."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    brand_color = models.CharField(max_length=7, default="#714B67")
    industry = models.CharField(
        max_length=20,
        choices=Industry.choices,
    )
    is_active = models.BooleanField(default=True)
    config_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "companies"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extends Django User with company membership and preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="members",
    )
    phone = models.CharField(max_length=20, blank=True, default="")
    department = models.CharField(max_length=100, blank=True, default="")
    job_title = models.CharField(max_length=100, blank=True, default="")
    timezone = models.CharField(max_length=50, default="UTC")
    language = models.CharField(max_length=10, default="en")
    is_company_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.company.slug})"


class RoleLevel(models.TextChoices):
    OPERATIONAL = "L1", "Operational"
    SUPERVISOR = "L2", "Supervisor"
    MANAGER = "L3", "Manager"
    DIRECTOR = "L4", "Director"
    EXECUTIVE = "L5", "Executive"


class Permission(models.Model):
    """Module-level + action-level permission.

    codename format: '{module}.{action}' e.g. 'accounting.read'
    """

    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=50)
    action = models.CharField(max_length=20)

    class Meta:
        ordering = ["module", "action"]

    def __str__(self):
        return self.codename


class IndustryRoleTemplate(models.Model):
    """Pre-defined role template per industry.

    80 templates total (8 roles x 10 industries).
    Copied into company-specific Roles on provisioning.
    """

    industry = models.CharField(max_length=20, choices=Industry.choices)
    role_slug = models.SlugField(max_length=100)
    role_name = models.CharField(max_length=255)
    role_level = models.CharField(max_length=2, choices=RoleLevel.choices)
    module_permissions = models.JSONField(default=list)
    dashboard_config = models.JSONField(default=dict, blank=True)
    anomaly_alerts = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ["industry", "role_slug"]
        ordering = ["industry", "role_level", "role_name"]

    def __str__(self):
        return f"{self.get_industry_display()} — {self.role_name}"


class Role(TenantModel):
    """Company-specific role, optionally created from a template."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    is_system = models.BooleanField(default=False)
    role_level = models.CharField(max_length=2, choices=RoleLevel.choices)
    template = models.ForeignKey(
        IndustryRoleTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_roles",
    )
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        related_name="roles",
        blank=True,
    )
    dashboard_config = models.JSONField(default=dict, blank=True)
    anomaly_alerts = models.JSONField(default=list, blank=True)

    class Meta(TenantModel.Meta):
        unique_together = ["company", "name"]

    def __str__(self):
        return f"{self.name} ({self.company.slug})"


class RolePermission(models.Model):
    """Links a Role to a Permission."""

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["role", "permission"]

    def __str__(self):
        return f"{self.role.name} → {self.permission.codename}"


class UserRole(models.Model):
    """Assigns a Role to a User within a company."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")

    class Meta:
        unique_together = ["user", "role"]

    def __str__(self):
        return f"{self.user.username} → {self.role.name}"


# ─── Module System ──────────────────────────────────────────────


class ModuleRegistry(TenantModel):
    """Tracks which modules are installed per company."""

    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, default="")
    is_installed = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)
    sequence = models.IntegerField(default=0)
    color = models.CharField(max_length=7, blank=True, default="")

    class Meta(TenantModel.Meta):
        unique_together = ["company", "name"]
        ordering = ["sequence", "display_name"]
        verbose_name_plural = "module registries"

    def __str__(self):
        return f"{self.display_name} ({self.company.slug})"


class ModuleConfig(TenantModel):
    """Per-company module configuration key-value pairs."""

    module = models.ForeignKey(
        ModuleRegistry,
        on_delete=models.CASCADE,
        related_name="configs",
    )
    key = models.CharField(max_length=100)
    value = models.TextField(blank=True, default="")
    value_type = models.CharField(
        max_length=10,
        choices=[
            ("string", "String"),
            ("int", "Integer"),
            ("bool", "Boolean"),
            ("json", "JSON"),
        ],
        default="string",
    )

    class Meta(TenantModel.Meta):
        unique_together = ["company", "module", "key"]

    def __str__(self):
        return f"{self.module.name}.{self.key}"


class Menu(TenantModel):
    """Navigation menu items per company/module."""

    module = models.ForeignKey(
        ModuleRegistry,
        on_delete=models.CASCADE,
        related_name="menus",
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, default="")
    sequence = models.IntegerField(default=0)
    url = models.CharField(max_length=255, blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["sequence", "label"]

    def __str__(self):
        return self.label


# ─── View System ───────────────────────────────────────────────


class ViewType(models.TextChoices):
    LIST = "list", "List"
    FORM = "form", "Form"
    KANBAN = "kanban", "Kanban"
    PIVOT = "pivot", "Pivot"
    GRAPH = "graph", "Graph"


class ViewDefinition(TenantModel):
    """JSON-driven view configuration (Odoo-style).

    Stores how to render a list, form, kanban, pivot, or graph view
    for a given model. The frontend reads the config and renders the
    appropriate component.
    """

    model_name = models.CharField(max_length=100)
    view_type = models.CharField(max_length=10, choices=ViewType.choices)
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    priority = models.IntegerField(default=16)
    config = models.JSONField(default=dict)

    class Meta(TenantModel.Meta):
        ordering = ["model_name", "priority"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "model_name", "view_type"],
                condition=models.Q(is_default=True, deleted_at__isnull=True),
                name="unique_default_view_per_model_type",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.view_type})"


# ─── Sequence System ────────────────────────────────────────────


class Sequence(models.Model):
    """Auto-incrementing sequence per company and prefix.

    Generates IDs like INV/2026/00001, PO/2026/00002.
    Uses select_for_update() for thread-safety.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="sequences",
    )
    prefix = models.CharField(max_length=20)
    suffix = models.CharField(max_length=20, blank=True, default="")
    next_number = models.PositiveIntegerField(default=1)
    step = models.PositiveIntegerField(default=1)
    padding = models.PositiveIntegerField(default=5)
    use_date_range = models.BooleanField(default=True)
    reset_period = models.CharField(
        max_length=10,
        choices=[("yearly", "Yearly"), ("monthly", "Monthly"), ("never", "Never")],
        default="yearly",
    )

    class Meta:
        unique_together = ["company", "prefix"]

    def __str__(self):
        return f"{self.prefix} ({self.company.slug})"


# ─── Audit + Notification ───────────────────────────────────────


class AuditLog(models.Model):
    """Immutable audit trail for all model changes."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    model_name = models.CharField(max_length=100)
    model_id = models.PositiveIntegerField()
    action = models.CharField(
        max_length=10,
        choices=[
            ("create", "Create"),
            ("update", "Update"),
            ("delete", "Delete"),
        ],
    )
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} {self.model_name}#{self.model_id}"


class Notification(models.Model):
    """In-app notification for a user."""

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, default="")
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ("info", "Info"),
            ("warning", "Warning"),
            ("error", "Error"),
            ("success", "Success"),
        ],
        default="info",
    )
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True, default="")
    related_model = models.CharField(max_length=100, blank=True, default="")
    related_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} → {self.recipient.username}"


class IndustryConfigTemplate(models.Model):
    """Industry-level config defaults. One row per industry, loaded from YAML files.

    Forms the base of the 3-tier hierarchy:
    IndustryConfigTemplate → Company.config_json → ModuleConfig (most specific)
    """

    industry = models.CharField(
        max_length=20,
        choices=Industry.choices,
        unique=True,
    )
    config = models.JSONField(
        default=dict,
        help_text="Full config dict including terminology, module overrides, and defaults.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["industry"]

    def __str__(self):
        return f"Config: {self.get_industry_display()}"


class Partner(TenantModel):
    """Unified customer + vendor entity (Odoo-style, D21).

    A Partner can be a customer (receives invoices), a vendor (issues them),
    or both. Replaces per-module `customer_name` CharField and per-module
    Vendor tables with a single source of truth per company.
    """

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=40, blank=True, default="")
    is_customer = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    tax_id = models.CharField(max_length=64, blank=True, default="")
    payment_terms_days = models.PositiveIntegerField(default=0)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    industry_tags = models.JSONField(default=list, blank=True)
    address_json = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name", "tax_id"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_partner_name_tax_id_per_company",
            ),
        ]

    def __str__(self):
        return self.name


class Setting(models.Model):
    """Global or per-company settings."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="settings",
        null=True,
        blank=True,
    )
    key = models.CharField(max_length=100)
    value = models.TextField(blank=True, default="")
    value_type = models.CharField(
        max_length=10,
        choices=[
            ("string", "String"),
            ("int", "Integer"),
            ("bool", "Boolean"),
            ("json", "JSON"),
        ],
        default="string",
    )

    class Meta:
        unique_together = ["company", "key"]

    def __str__(self):
        scope = self.company.slug if self.company else "global"
        return f"{self.key} ({scope})"


class CompanyWebhookConfig(models.Model):
    """Per-company webhook peer + shared HMAC secret (Slice 22, D38).

    See docs/CALENDAR-SYNC-WEBHOOKS.md §Configuration. Holds the URL we
    POST outbound webhooks to (the peer's receiver), the HMAC secret
    shared with that peer for signing/verifying both directions, and
    status fields used by the emitter to record success / error state.

    One row per company — webhooks are tenant-scoped end-to-end.
    """

    company = models.OneToOneField(
        "core.Company",
        on_delete=models.CASCADE,
        related_name="webhook_config",
    )
    peer_url = models.URLField(
        max_length=500,
        help_text=(
            "Where outbound webhooks are POSTed. Example: "
            "https://crm.novapay.com/api/v1/webhooks/calendar/novapay/"
        ),
    )
    shared_secret = models.CharField(
        max_length=128,
        help_text="32+ byte hex key shared with the peer. Used for HMAC sign + verify.",
    )
    enabled = models.BooleanField(
        default=False,
        help_text="When False, both inbound and outbound webhooks are no-ops.",
    )
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)
    last_error_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        state = "enabled" if self.enabled else "disabled"
        return f"WebhookConfig({self.company.slug}, {state})"
