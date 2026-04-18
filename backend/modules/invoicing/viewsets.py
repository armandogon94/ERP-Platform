from rest_framework import viewsets

from api.v1.aggregation import AggregationMixin
from api.v1.filters import CompanyScopedFilterBackend
from api.v1.mixins import FilterParamsMixin
from api.v1.permissions import IsCompanyMember
from modules.invoicing.models import CreditNote, Invoice, InvoiceLine
from modules.invoicing.serializers import (
    CreditNoteSerializer,
    InvoiceLineSerializer,
    InvoiceSerializer,
)


class InvoiceViewSet(FilterParamsMixin, AggregationMixin, viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    # REVIEW I-8: select_related prevents N+1 once serializers touch
    # customer.<attr>. Denormalized customer_name still keeps the list
    # cheap today, but the join is free insurance against future reads.
    queryset = Invoice.objects.select_related("customer").order_by(
        "-invoice_date", "-created_at"
    )
    filter_params = {"status": "status", "invoice_type": "invoice_type"}

    aggregatable_fields = frozenset(
        {"status", "invoice_type", "customer", "invoice_date", "due_date"}
    )
    aggregatable_measures = frozenset(
        {"subtotal", "tax_amount", "total_amount", "amount_paid"}
    )

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class InvoiceLineViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = InvoiceLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = InvoiceLine.objects.order_by("pk")
    filter_params = {"invoice": "invoice_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class CreditNoteViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = CreditNoteSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = CreditNote.objects.select_related("invoice").order_by("-created_at")
    filter_params = {"invoice": "invoice_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
