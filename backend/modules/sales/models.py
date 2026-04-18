"""Sales module models: SalesQuotation, SalesOrder, SalesOrderLine."""

from django.db import models

from core.models import TenantModel
from core.sequence import get_next_sequence


class SalesQuotation(TenantModel):
    """A quotation sent to a customer before converting to a sales order."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"

    quotation_number = models.CharField(max_length=100, blank=True, default="")
    # REVIEW I-10 / D21: `customer` is canonical; `customer_name`/
    # `customer_email` are intentional denormalized snapshots (list-view
    # perf + historical integrity + one-off customer support). save()
    # populates them from the FK when blank.
    customer = models.ForeignKey(
        "core.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    customer_name = models.CharField(max_length=300, blank=True, default="")
    customer_email = models.EmailField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    total_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.quotation_number and self.company_id:
            self.quotation_number = get_next_sequence(self.company, "QUO")
        # REVIEW I-10: backfill denormalized customer fields from the FK.
        if self.customer_id:
            if not self.customer_name:
                self.customer_name = self.customer.name or ""
            if not self.customer_email:
                self.customer_email = self.customer.email or ""
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.quotation_number or f"QUO-{self.pk}"


class SalesOrder(TenantModel):
    """A confirmed sales order."""

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        DELIVERED = "delivered", "Delivered"
        INVOICED = "invoiced", "Invoiced"
        CANCELLED = "cancelled", "Cancelled"

    order_number = models.CharField(max_length=100, blank=True, default="")
    # REVIEW I-10 / D21: see SalesQuotation for denormalization rationale.
    customer = models.ForeignKey(
        "core.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    customer_name = models.CharField(max_length=300, blank=True, default="")
    customer_email = models.EmailField(blank=True, default="")
    quotation = models.OneToOneField(
        SalesQuotation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_order",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    order_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    total_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number and self.company_id:
            self.order_number = get_next_sequence(self.company, "SO")
        if self.customer_id:
            if not self.customer_name:
                self.customer_name = self.customer.name or ""
            if not self.customer_email:
                self.customer_email = self.customer.email or ""
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.order_number or f"SO-{self.pk}"


class SalesOrderLine(TenantModel):
    """A single line item on a sales order."""

    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    description = models.CharField(max_length=500, blank=True, default="")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["pk"]

    def __str__(self) -> str:
        return f"{self.description} x{self.quantity}"
