"""Point of Sale module models: POSSession, POSOrder, POSOrderLine, CashMovement."""

from django.conf import settings
from django.db import models

from core.models import TenantModel
from core.sequence import get_next_sequence


class POSSession(TenantModel):
    """A cash-drawer session on a physical station."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    station = models.CharField(max_length=100)
    cash_on_open = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_on_close = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    expected_cash = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    variance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    notes = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["-opened_at"]

    def __str__(self) -> str:
        return f"Session {self.station} ({self.status})"


class POSOrder(TenantModel):
    """A single point-of-sale order."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PAID = "paid", "Paid"
        REFUNDED = "refunded", "Refunded"

    session = models.ForeignKey(
        POSSession, on_delete=models.PROTECT, related_name="orders"
    )
    order_number = models.CharField(max_length=100, blank=True, default="")
    customer = models.ForeignKey(
        "core.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    notes = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number and self.company_id:
            self.order_number = get_next_sequence(self.company, "POS")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.order_number or f"POS-{self.pk}"


class POSOrderLine(TenantModel):
    """A single product line on a POS order."""

    order = models.ForeignKey(
        POSOrder, on_delete=models.CASCADE, related_name="lines"
    )
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        related_name="pos_lines",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta(TenantModel.Meta):
        ordering = ["order", "-created_at"]

    def __str__(self) -> str:
        return f"{self.quantity} × {self.product.name}"


class CashMovement(TenantModel):
    """A cash drawer adjustment (pay-in or pay-out) during a session."""

    class MovementType(models.TextChoices):
        IN = "in", "In"
        OUT = "out", "Out"

    session = models.ForeignKey(
        POSSession, on_delete=models.CASCADE, related_name="cash_movements"
    )
    type = models.CharField(
        max_length=5, choices=MovementType.choices, default=MovementType.IN
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reason = models.CharField(max_length=255, blank=True, default="")
    at_time = models.DateTimeField(auto_now_add=True)

    class Meta(TenantModel.Meta):
        ordering = ["-at_time"]

    def __str__(self) -> str:
        sign = "+" if self.type == self.MovementType.IN else "-"
        return f"{sign}{self.amount} — {self.reason}"
