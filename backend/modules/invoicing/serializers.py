from rest_framework import serializers

from modules.invoicing.models import CreditNote, Invoice, InvoiceLine


class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        fields = [
            "id",
            "invoice",
            "description",
            "quantity",
            "unit_price",
            "tax_rate",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "invoice_type",
            "status",
            "customer",
            "customer_name",
            "customer_email",
            "invoice_date",
            "due_date",
            "notes",
            "subtotal",
            "tax_amount",
            "total_amount",
            "amount_paid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        partner = attrs.get("customer")
        if partner and not attrs.get("customer_name"):
            attrs["customer_name"] = partner.name
        return attrs


class CreditNoteSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(
        source="invoice.invoice_number", read_only=True
    )

    class Meta:
        model = CreditNote
        fields = [
            "id",
            "credit_note_number",
            "invoice",
            "invoice_number",
            "reason",
            "amount",
            "issue_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "invoice_number", "created_at", "updated_at"]
