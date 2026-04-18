from rest_framework import viewsets

from api.v1.aggregation import AggregationMixin
from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.sales.models import SalesOrder, SalesOrderLine, SalesQuotation
from modules.sales.serializers import (
    SalesOrderLineSerializer,
    SalesOrderSerializer,
    SalesQuotationSerializer,
)


class SalesQuotationViewSet(AggregationMixin, viewsets.ModelViewSet):
    serializer_class = SalesQuotationSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = SalesQuotation.objects.order_by("-created_at")

    aggregatable_fields = frozenset({"status", "customer", "valid_until"})
    aggregatable_measures = frozenset({"total_amount"})

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


class SalesOrderViewSet(AggregationMixin, viewsets.ModelViewSet):
    serializer_class = SalesOrderSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = SalesOrder.objects.order_by("-created_at")

    aggregatable_fields = frozenset(
        {"status", "customer", "order_date", "delivery_date"}
    )
    aggregatable_measures = frozenset({"total_amount"})

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


class SalesOrderLineViewSet(viewsets.ModelViewSet):
    serializer_class = SalesOrderLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = SalesOrderLine.objects.order_by("pk")

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        sales_order = self.request.query_params.get("sales_order")
        if sales_order:
            qs = qs.filter(sales_order_id=sales_order)
        return qs
