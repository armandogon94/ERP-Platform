"""Purchasing module models: Vendor, PurchaseOrder, POLine."""

from django.db import models

from core.models import TenantModel


class Vendor(TenantModel):
    """A supplier or vendor from whom goods/services are purchased."""

    class PaymentTerms(models.TextChoices):
        IMMEDIATE = "immediate", "Immediate"
        NET_15 = "net_15", "Net 15"
        NET_30 = "net_30", "Net 30"
        NET_60 = "net_60", "Net 60"
        NET_90 = "net_90", "Net 90"

    name = models.CharField(max_length=300)
    email = models.EmailField(blank=True, default="")
    contact_name = models.CharField(max_length=200, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")
    currency = models.CharField(max_length=10, blank=True, default="USD")
    payment_terms = models.CharField(
        max_length=20,
        choices=PaymentTerms.choices,
        default=PaymentTerms.NET_30,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class PurchaseOrder(TenantModel):
    """A purchase order sent to a vendor."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        CONFIRMED = "confirmed", "Confirmed"
        RECEIVED = "received", "Received"
        CANCELLED = "cancelled", "Cancelled"

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name="purchase_orders",
    )
    partner = models.ForeignKey(
        "core.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    po_number = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    order_date = models.DateField(null=True, blank=True)
    expected_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    total_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=0
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.po_number or f"PO-{self.pk}"


class RequestForQuote(TenantModel):
    """A request for quote sent to a vendor before raising a purchase order."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        RECEIVED = "received", "Received"
        ACCEPTED = "accepted", "Accepted"
        CANCELLED = "cancelled", "Cancelled"

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name="rfqs",
    )
    rfq_number = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    request_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.rfq_number or f"RFQ-{self.pk}"


class RFQLine(TenantModel):
    """A single line item on a request for quote."""

    rfq = models.ForeignKey(
        RequestForQuote,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    description = models.CharField(max_length=500, blank=True, default="")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["pk"]

    def __str__(self) -> str:
        return f"{self.description} x{self.quantity}"


class POLine(TenantModel):
    """A single line item on a purchase order."""

    purchase_order = models.ForeignKey(
        PurchaseOrder,
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
