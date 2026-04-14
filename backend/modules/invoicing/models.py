"""Invoicing module models: Invoice, InvoiceLine, CreditNote."""

from django.db import models

from core.models import TenantModel


class Invoice(TenantModel):
    """A customer invoice or vendor bill."""

    class InvoiceType(models.TextChoices):
        CUSTOMER = "customer", "Customer Invoice"
        VENDOR = "vendor", "Vendor Bill"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        POSTED = "posted", "Posted"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    invoice_number = models.CharField(max_length=100, blank=True, default="")
    invoice_type = models.CharField(
        max_length=20,
        choices=InvoiceType.choices,
        default=InvoiceType.CUSTOMER,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    customer_name = models.CharField(max_length=300, blank=True, default="")
    customer_email = models.EmailField(blank=True, default="")
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-invoice_date", "-created_at"]

    def __str__(self) -> str:
        return self.invoice_number or f"INV-{self.pk}"


class InvoiceLine(TenantModel):
    """A single line item on an invoice."""

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    description = models.CharField(max_length=500, blank=True, default="")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Tax rate as a percentage, e.g. 10 for 10%",
    )
    total_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["pk"]

    def __str__(self) -> str:
        return self.description or f"Line {self.pk}"


class CreditNote(TenantModel):
    """A credit note issued against an invoice (full or partial reversal)."""

    credit_note_number = models.CharField(max_length=100, blank=True, default="")
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="credit_notes",
    )
    reason = models.TextField(blank=True, default="")
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    issue_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.credit_note_number or f"CN-{self.pk}"
