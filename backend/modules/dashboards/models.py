"""Dashboard models.

A ``Dashboard`` is a named collection of ``DashboardWidget`` rows. Each widget
fetches its data from a named **data source** (see ``data_sources.py``) — the
source name is a registry key, never direct SQL from the client.

D6 / per-industry richness: industry YAML presets in ``industry_presets/``
seed an initial ``Dashboard`` + ``DashboardWidget`` set per company. Users
can later rearrange / add / remove widgets (future iteration — v1 seeds and
renders; in-UI editing is out of scope).
"""

from django.db import models

from core.models import TenantModel


class Dashboard(TenantModel):
    """A named dashboard view composed of ordered widgets."""

    name = models.CharField(max_length=120, default="Home")
    slug = models.SlugField(max_length=120)
    is_default = models.BooleanField(
        default=False,
        help_text="Shown at /dashboard when no slug is specified.",
    )
    industry_preset = models.CharField(
        max_length=60,
        blank=True,
        default="",
        help_text=(
            "Tracks which industry YAML preset seeded this dashboard. "
            "Lets us re-seed a tenant's default dashboard after a preset bump."
        ),
    )
    layout_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Positions / sizes when we add drag-to-rearrange (future).",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "slug"], name="dashboard_company_slug_uniq"
            ),
            # Only one default dashboard per company.
            models.UniqueConstraint(
                fields=["company"],
                condition=models.Q(is_default=True),
                name="dashboard_company_one_default",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"


class DashboardWidget(TenantModel):
    """One tile / chart on a ``Dashboard``."""

    class WidgetType(models.TextChoices):
        KPI = "kpi", "KPI tile (big number + optional detail)"
        BAR = "bar", "Bar chart"
        LINE = "line", "Line chart"
        PIE = "pie", "Pie chart"
        AREA = "area", "Area chart"
        TABLE = "table", "Ranked list / table"

    dashboard = models.ForeignKey(
        Dashboard, on_delete=models.CASCADE, related_name="widgets"
    )
    position = models.PositiveIntegerField(default=0)
    widget_type = models.CharField(
        max_length=20, choices=WidgetType.choices, default=WidgetType.KPI
    )
    title = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=240, blank=True, default="")
    data_source = models.CharField(
        max_length=120,
        help_text=(
            "Registry key — see modules.dashboards.data_sources. "
            "Not user-editable raw SQL; always a whitelisted aggregate."
        ),
    )
    config_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Widget-type-specific config plus data-source parameters. "
            "Shape examples: {\"period\": \"last_30_days\", \"limit\": 5}."
        ),
    )

    class Meta:
        ordering = ["dashboard", "position", "pk"]

    def __str__(self) -> str:
        return f"{self.title} ({self.widget_type})"
