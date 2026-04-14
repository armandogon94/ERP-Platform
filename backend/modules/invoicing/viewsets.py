from rest_framework import viewsets

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.invoicing.models import CreditNote, Invoice, InvoiceLine
from modules.invoicing.serializers import (
    CreditNoteSerializer,
    InvoiceLineSerializer,
    InvoiceSerializer,
)


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Invoice.objects.order_by("-invoice_date", "-created_at")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        invoice_type = self.request.query_params.get("invoice_type")
        if invoice_type:
            qs = qs.filter(invoice_type=invoice_type)
        return qs


class InvoiceLineViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = InvoiceLine.objects.order_by("pk")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        invoice = self.request.query_params.get("invoice")
        if invoice:
            qs = qs.filter(invoice_id=invoice)
        return qs


class CreditNoteViewSet(viewsets.ModelViewSet):
    serializer_class = CreditNoteSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = CreditNote.objects.select_related("invoice").order_by("-created_at")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        invoice = self.request.query_params.get("invoice")
        if invoice:
            qs = qs.filter(invoice_id=invoice)
        return qs
