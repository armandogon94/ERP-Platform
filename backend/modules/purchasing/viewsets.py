from rest_framework import viewsets

from api.v1.aggregation import AggregationMixin
from api.v1.filters import CompanyScopedFilterBackend
from api.v1.mixins import FilterParamsMixin
from api.v1.permissions import IsCompanyMember
from modules.purchasing.models import POLine, PurchaseOrder, RequestForQuote, RFQLine, Vendor
from modules.purchasing.serializers import (
    POLineSerializer,
    PurchaseOrderSerializer,
    RequestForQuoteSerializer,
    RFQLineSerializer,
    VendorSerializer,
)


class VendorViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = VendorSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Vendor.objects.order_by("name")
    filter_params = {"is_active": "is_active__bool"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class PurchaseOrderViewSet(FilterParamsMixin, AggregationMixin, viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    # REVIEW I-8: include partner in the join — PurchaseOrder has both
    # vendor (denormalized legacy) and partner (canonical Slice 10.6) FKs.
    queryset = PurchaseOrder.objects.select_related("vendor", "partner").order_by(
        "-created_at"
    )
    filter_params = {"status": "status", "vendor": "vendor_id"}

    aggregatable_fields = frozenset(
        {"status", "vendor", "partner", "order_date", "expected_date"}
    )
    aggregatable_measures = frozenset({"total_amount"})

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class POLineViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = POLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = POLine.objects.order_by("pk")
    filter_params = {"purchase_order": "purchase_order_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class RequestForQuoteViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = RequestForQuoteSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = RequestForQuote.objects.select_related("vendor").order_by("-created_at")
    filter_params = {"status": "status", "vendor": "vendor_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class RFQLineViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = RFQLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = RFQLine.objects.order_by("pk")
    filter_params = {"rfq": "rfq_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
