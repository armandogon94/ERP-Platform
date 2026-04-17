"""Reports module models: ReportTemplate, PivotDefinition, ScheduledExport."""

from django.db import models

from core.models import TenantModel


class ReportTemplate(TenantModel):
    """A saved report definition (which model, default filters/groups/measures)."""

    name = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)
    default_filters = models.JSONField(default=dict, blank=True)
    default_group_by = models.JSONField(default=list, blank=True)
    default_measures = models.JSONField(default=list, blank=True)
    industry_tag = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class PivotDefinition(TenantModel):
    """A saved pivot-table config for a given model."""

    name = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)
    rows = models.JSONField(default=list, blank=True)
    cols = models.JSONField(default=list, blank=True)
    measure = models.CharField(max_length=100)
    aggregator = models.CharField(max_length=20, default="sum")

    class Meta(TenantModel.Meta):
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ScheduledExport(TenantModel):
    """A scheduled report export (CSV/PDF/XLSX) sent to recipients on a cron."""

    class Format(models.TextChoices):
        PDF = "pdf", "PDF"
        CSV = "csv", "CSV"
        XLSX = "xlsx", "Excel"

    report = models.ForeignKey(
        ReportTemplate, on_delete=models.CASCADE, related_name="scheduled_exports"
    )
    cron = models.CharField(max_length=100, default="0 8 * * 1")
    format = models.CharField(
        max_length=10, choices=Format.choices, default=Format.PDF
    )
    recipients = models.JSONField(default=list, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta(TenantModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.report.name} → {self.format}"
