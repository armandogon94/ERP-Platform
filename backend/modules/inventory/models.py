"""Inventory module models: ProductCategory, Product, StockLocation,
StockLot, StockMove, ReorderRule."""

from django.db import models

from core.models import TenantModel


class ProductCategory(TenantModel):
    """Hierarchical product categorization."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "product categories"

    def __str__(self) -> str:
        return self.name


class Product(TenantModel):
    """An inventory item — goods or materials tracked in stock."""

    class UOM(models.TextChoices):
        EACH = "each", "Each"
        BOX = "box", "Box"
        CASE = "case", "Case"
        KG = "kg", "Kilogram"
        LITER = "liter", "Liter"
        METER = "meter", "Meter"

    name = models.CharField(max_length=300)
    sku = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    unit_of_measure = models.CharField(
        max_length=20,
        choices=UOM.choices,
        default=UOM.EACH,
    )
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    sale_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    reorder_point = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Stock level that triggers a reorder rule",
    )
    min_stock_level = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["company", "sku"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})" if self.sku else self.name


class StockLocation(TenantModel):
    """A physical or virtual location where stock is stored."""

    class LocationType(models.TextChoices):
        INTERNAL = "internal", "Internal"
        SUPPLIER = "supplier", "Supplier"
        CUSTOMER = "customer", "Customer"
        TRANSIT = "transit", "Transit"
        VIRTUAL = "virtual", "Virtual"

    name = models.CharField(max_length=200)
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices,
        default=LocationType.INTERNAL,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_locations",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} [{self.get_location_type_display()}]"


class StockLot(TenantModel):
    """A lot or batch of a product for traceability and expiry tracking."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="lots",
    )
    lot_number = models.CharField(max_length=100)
    expiry_date = models.DateField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-expiry_date", "lot_number"]
        unique_together = ["product", "lot_number"]

    def __str__(self) -> str:
        return f"Lot {self.lot_number} — {self.product.name}"


class StockMove(TenantModel):
    """A stock movement (receipt, delivery, internal transfer, adjustment)."""

    class MoveType(models.TextChoices):
        RECEIPT = "receipt", "Receipt"
        DELIVERY = "delivery", "Delivery"
        INTERNAL = "internal", "Internal Transfer"
        ADJUSTMENT = "adjustment", "Inventory Adjustment"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_moves",
    )
    source_location = models.ForeignKey(
        StockLocation,
        on_delete=models.PROTECT,
        related_name="outgoing_moves",
    )
    destination_location = models.ForeignKey(
        StockLocation,
        on_delete=models.PROTECT,
        related_name="incoming_moves",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    lot = models.ForeignKey(
        StockLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moves",
    )
    move_type = models.CharField(
        max_length=20,
        choices=MoveType.choices,
        default=MoveType.INTERNAL,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    reference = models.CharField(max_length=200, blank=True, default="")
    move_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-move_date", "-created_at"]

    def __str__(self) -> str:
        return (
            f"{self.get_move_type_display()} — {self.product.name} "
            f"x{self.quantity}"
        )


class ReorderRule(TenantModel):
    """Automatic reorder trigger when stock drops below a threshold."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reorder_rules",
    )
    location = models.ForeignKey(
        StockLocation,
        on_delete=models.CASCADE,
        related_name="reorder_rules",
    )
    min_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["product__name"]
        unique_together = ["product", "location"]

    def __str__(self) -> str:
        return (
            f"Reorder: {self.product.name} @ {self.location.name} "
            f"(min {self.min_quantity})"
        )
