"""Manufacturing module models: BillOfMaterials, BOMLine, WorkOrder, ProductionCost."""

from django.db import models

from core.models import TenantModel


class BillOfMaterials(TenantModel):
    """The list of components needed to produce one unit of a finished product."""

    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        related_name="boms",
    )
    version = models.CharField(max_length=20, default="1.0")
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["product", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "product", "version"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_bom_product_version_per_company",
            ),
        ]

    def __str__(self) -> str:
        return f"BOM {self.product.name} v{self.version}"


class BOMLine(TenantModel):
    """A single component consumed by a BOM."""

    bom = models.ForeignKey(
        BillOfMaterials, on_delete=models.CASCADE, related_name="lines"
    )
    component = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        related_name="bom_lines",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    uom = models.CharField(max_length=20, blank=True, default="unit")

    class Meta(TenantModel.Meta):
        ordering = ["bom", "-created_at"]

    def __str__(self) -> str:
        return f"{self.quantity} × {self.component.name}"


class WorkOrder(TenantModel):
    """A manufacturing run producing finished product from components."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        related_name="work_orders",
    )
    bom = models.ForeignKey(
        BillOfMaterials,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="work_orders",
    )
    quantity_target = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    quantity_done = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"WO {self.product.name} × {self.quantity_target}"


class ProductionCost(TenantModel):
    """A cost line attributed to a work order (material, labor, overhead)."""

    class CostType(models.TextChoices):
        MATERIAL = "material", "Material"
        LABOR = "labor", "Labor"
        OVERHEAD = "overhead", "Overhead"

    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE, related_name="costs"
    )
    cost_type = models.CharField(
        max_length=20, choices=CostType.choices, default=CostType.MATERIAL
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_cost_type_display()}: {self.amount}"
