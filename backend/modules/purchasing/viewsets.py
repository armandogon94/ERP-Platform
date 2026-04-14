from rest_framework import viewsets

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.purchasing.models import POLine, PurchaseOrder, RequestForQuote, RFQLine, Vendor
from modules.purchasing.serializers import (
    POLineSerializer,
    PurchaseOrderSerializer,
    RequestForQuoteSerializer,
    RFQLineSerializer,
    VendorSerializer,
)


class VendorViewSet(viewsets.ModelViewSet):
    serializer_class = VendorSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Vendor.objects.order_by("name")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = PurchaseOrder.objects.select_related("vendor").order_by("-created_at")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        vendor = self.request.query_params.get("vendor")
        if vendor:
            qs = qs.filter(vendor_id=vendor)
        return qs


class POLineViewSet(viewsets.ModelViewSet):
    serializer_class = POLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = POLine.objects.order_by("pk")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        purchase_order = self.request.query_params.get("purchase_order")
        if purchase_order:
            qs = qs.filter(purchase_order_id=purchase_order)
        return qs


class RequestForQuoteViewSet(viewsets.ModelViewSet):
    serializer_class = RequestForQuoteSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = RequestForQuote.objects.select_related("vendor").order_by("-created_at")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        vendor = self.request.query_params.get("vendor")
        if vendor:
            qs = qs.filter(vendor_id=vendor)
        return qs


class RFQLineViewSet(viewsets.ModelViewSet):
    serializer_class = RFQLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = RFQLine.objects.order_by("pk")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        rfq = self.request.query_params.get("rfq")
        if rfq:
            qs = qs.filter(rfq_id=rfq)
        return qs
