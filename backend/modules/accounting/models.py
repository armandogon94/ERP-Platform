"""Accounting module models: Account (CoA), Journal, JournalEntry, JournalEntryLine."""

from django.db import models

from core.models import TenantModel


class Account(TenantModel):
    """A chart-of-accounts entry — one account in the general ledger."""

    class AccountType(models.TextChoices):
        ASSET = "asset", "Asset"
        LIABILITY = "liability", "Liability"
        EQUITY = "equity", "Equity"
        REVENUE = "revenue", "Revenue"
        EXPENSE = "expense", "Expense"

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=300)
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.ASSET,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        unique_together = ["company", "code"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class Journal(TenantModel):
    """A journal groups related entries (general, sales, purchases, cash, bank)."""

    class JournalType(models.TextChoices):
        GENERAL = "general", "General"
        SALE = "sale", "Sale"
        PURCHASE = "purchase", "Purchase"
        CASH = "cash", "Cash"
        BANK = "bank", "Bank"

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    journal_type = models.CharField(
        max_length=20,
        choices=JournalType.choices,
        default=JournalType.GENERAL,
    )
    default_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_journals",
    )

    class Meta:
        ordering = ["name"]
        unique_together = ["company", "code"]

    def __str__(self) -> str:
        return self.name


class JournalEntry(TenantModel):
    """A journal entry (transaction) containing balanced debit/credit lines."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        POSTED = "posted", "Posted"
        CANCELLED = "cancelled", "Cancelled"

    journal = models.ForeignKey(
        Journal,
        on_delete=models.PROTECT,
        related_name="entries",
    )
    reference = models.CharField(max_length=100, blank=True, default="")
    entry_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-entry_date", "-created_at"]

    def __str__(self) -> str:
        return self.reference or f"JE-{self.pk}"


class JournalEntryLine(TenantModel):
    """A single debit or credit line within a journal entry."""

    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="entry_lines",
    )
    label = models.CharField(max_length=300, blank=True, default="")
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["pk"]

    def __str__(self) -> str:
        return self.label or f"Line {self.pk}"
