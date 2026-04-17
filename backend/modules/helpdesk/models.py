"""Helpdesk module models: TicketCategory, SLAConfig, Ticket, KnowledgeArticle."""

from django.conf import settings
from django.db import models

from core.models import TenantModel
from core.sequence import get_next_sequence


class TicketCategory(TenantModel):
    """A grouping of support tickets (Billing, Technical, Clinical, etc.)."""

    name = models.CharField(max_length=100)
    sla_hours = models.PositiveIntegerField(default=24)
    industry_tag = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_category_name_per_company",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class SLAConfig(TenantModel):
    """SLA thresholds for a given category + priority."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    category = models.ForeignKey(
        TicketCategory, on_delete=models.CASCADE, related_name="sla_configs"
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )
    response_hours = models.PositiveIntegerField(default=4)
    resolution_hours = models.PositiveIntegerField(default=24)

    class Meta(TenantModel.Meta):
        ordering = ["category", "priority"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "category", "priority"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_sla_per_category_priority",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.category.name} / {self.priority}"


class Ticket(TenantModel):
    """A support ticket raised against the company."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    ticket_number = models.CharField(max_length=100, blank=True, default="")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.ForeignKey(
        TicketCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tickets",
    )
    reporter_partner = models.ForeignKey(
        "core.Partner",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    reporter_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="helpdesk_reported",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="helpdesk_assigned",
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    sla_breached = models.BooleanField(default=False)

    class Meta(TenantModel.Meta):
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.ticket_number and self.company_id:
            self.ticket_number = get_next_sequence(self.company, "TKT")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.ticket_number or f"TKT-{self.pk}"


class KnowledgeArticle(TenantModel):
    """A knowledge base article supporting self-service."""

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=200)
    body = models.TextField(blank=True, default="")
    category = models.ForeignKey(
        TicketCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles",
    )
    published = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)

    class Meta(TenantModel.Meta):
        ordering = ["title"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "slug"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_article_slug_per_company",
            ),
        ]

    def __str__(self) -> str:
        return self.title
