"""Invoicing module models: Invoice, InvoiceLine, CreditNote."""

from django.db import models

from core.models import TenantModel
from core.sequence import get_next_sequence


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
    # REVIEW I-10 / D21: the `customer` FK is the canonical identity. The
    # `customer_name` and `customer_email` CharFields are INTENTIONALLY kept
    # as denormalized copies so that:
    #   (1) list views render without a Partner JOIN (perf);
    #   (2) the invoice preserves the name as it was at issue time, even
    #       if the Partner is later renamed (historical integrity —
    #       matches Odoo's "commercial_partner" snapshot pattern);
    #   (3) invoices can be issued to one-off customers without creating
    #       a Partner record.
    # Serializers populate `customer_name` from `customer.name` on save if
    # left blank; explicit values are respected.
    customer = models.ForeignKey(
        "core.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
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

    def save(self, *args, **kwargs):
        if not self.invoice_number and self.company_id:
            self.invoice_number = get_next_sequence(self.company, "INV")
        # REVIEW I-10: if customer FK is set but denormalized name/email is
        # blank, populate them at save time. Explicit values win (one-off
        # customers, historical snapshots).
        if self.customer_id:
            if not self.customer_name:
                self.customer_name = self.customer.name or ""
            if not self.customer_email:
                self.customer_email = self.customer.email or ""
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        # REVIEW I-11: total_price is a stored column for query performance
        # but the source of truth is quantity × unit_price × (1 + tax_rate/100).
        # Compute on save so a caller that forgets to populate it can't
        # silently corrupt invoice totals. Callers that DO pass an explicit
        # total are respected iff it matches the computed value within
        # rounding tolerance; otherwise the computed value wins and the
        # caller's value is logged as a divergence (no-op here — the
        # computed value simply replaces it).
        quantity = self.quantity or 0
        unit_price = self.unit_price or 0
        tax_rate = self.tax_rate or 0
        from decimal import Decimal
        tax_multiplier = Decimal("1") + (Decimal(tax_rate) / Decimal("100"))
        self.total_price = (Decimal(quantity) * Decimal(unit_price) * tax_multiplier).quantize(
            Decimal("0.01")
        )
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        if not self.credit_note_number and self.company_id:
            self.credit_note_number = get_next_sequence(self.company, "CN")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.credit_note_number or f"CN-{self.pk}"
