from rest_framework import viewsets

from api.v1.aggregation import AggregationMixin
from api.v1.filters import CompanyScopedFilterBackend
from api.v1.mixins import FilterParamsMixin
from api.v1.permissions import IsCompanyMember
from modules.inventory.models import (
    Product,
    ProductCategory,
    ReorderRule,
    StockLocation,
    StockLot,
    StockMove,
)
from modules.inventory.serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    ReorderRuleSerializer,
    StockLocationSerializer,
    StockLotSerializer,
    StockMoveSerializer,
)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ProductCategory.objects.order_by("name")

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class ProductViewSet(FilterParamsMixin, AggregationMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Product.objects.select_related("category").order_by("name")
    filter_params = {
        "is_active": "is_active__bool",
        "category": "category_id",
    }

    aggregatable_fields = frozenset({"category", "unit_of_measure", "is_active"})
    aggregatable_measures = frozenset({"sale_price", "cost_price", "reorder_point"})

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class StockLocationViewSet(viewsets.ModelViewSet):
    serializer_class = StockLocationSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = StockLocation.objects.order_by("name")

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class StockLotViewSet(viewsets.ModelViewSet):
    serializer_class = StockLotSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = StockLot.objects.select_related("product").order_by("-expiry_date")

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class StockMoveViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = StockMoveSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = StockMove.objects.select_related(
        "product", "source_location", "destination_location"
    ).order_by("-move_date", "-created_at")
    filter_params = {
        "status": "status",
        "move_type": "move_type",
        "product": "product_id",
    }

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class ReorderRuleViewSet(viewsets.ModelViewSet):
    serializer_class = ReorderRuleSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ReorderRule.objects.select_related("product", "location").order_by(
        "product__name"
    )

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
