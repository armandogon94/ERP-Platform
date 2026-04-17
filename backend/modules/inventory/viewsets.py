from rest_framework import viewsets

from api.v1.aggregation import AggregationMixin
from api.v1.filters import CompanyScopedFilterBackend
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
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class ProductViewSet(AggregationMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Product.objects.select_related("category").order_by("name")
    pagination_class = None

    aggregatable_fields = frozenset({"category", "unit_of_measure", "is_active"})
    aggregatable_measures = frozenset({"sale_price", "cost_price", "reorder_point"})

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category_id=category)

        return qs


class StockLocationViewSet(viewsets.ModelViewSet):
    serializer_class = StockLocationSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = StockLocation.objects.order_by("name")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class StockLotViewSet(viewsets.ModelViewSet):
    serializer_class = StockLotSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = StockLot.objects.select_related("product").order_by("-expiry_date")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class StockMoveViewSet(viewsets.ModelViewSet):
    serializer_class = StockMoveSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = StockMove.objects.select_related(
        "product", "source_location", "destination_location"
    ).order_by("-move_date", "-created_at")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()

        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)

        move_type = self.request.query_params.get("move_type")
        if move_type:
            qs = qs.filter(move_type=move_type)

        product = self.request.query_params.get("product")
        if product:
            qs = qs.filter(product_id=product)

        return qs


class ReorderRuleViewSet(viewsets.ModelViewSet):
    serializer_class = ReorderRuleSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ReorderRule.objects.select_related("product", "location").order_by(
        "product__name"
    )
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
