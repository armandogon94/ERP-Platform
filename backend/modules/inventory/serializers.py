from rest_framework import serializers

from modules.inventory.models import (
    Product,
    ProductCategory,
    ReorderRule,
    StockLocation,
    StockLot,
    StockMove,
)
from api.v1.serializer_fields import TenantScopedSerializerMixin


class ProductCategorySerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "description", "parent", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name", read_only=True, default=None
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "description",
            "category",
            "category_name",
            "unit_of_measure",
            "cost_price",
            "sale_price",
            "reorder_point",
            "min_stock_level",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "category_name", "created_at", "updated_at"]


class StockLocationSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = StockLocation
        fields = [
            "id",
            "name",
            "location_type",
            "parent",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StockLotSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = StockLot
        fields = [
            "id",
            "product",
            "product_name",
            "lot_number",
            "expiry_date",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "product_name", "created_at", "updated_at"]


class StockMoveSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    source_location_name = serializers.CharField(
        source="source_location.name", read_only=True
    )
    destination_location_name = serializers.CharField(
        source="destination_location.name", read_only=True
    )

    class Meta:
        model = StockMove
        fields = [
            "id",
            "product",
            "product_name",
            "source_location",
            "source_location_name",
            "destination_location",
            "destination_location_name",
            "quantity",
            "lot",
            "move_type",
            "status",
            "reference",
            "move_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "source_location_name",
            "destination_location_name",
            "created_at",
            "updated_at",
        ]


class ReorderRuleSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)

    class Meta:
        model = ReorderRule
        fields = [
            "id",
            "product",
            "product_name",
            "location",
            "location_name",
            "min_quantity",
            "max_quantity",
            "reorder_quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "product_name", "location_name", "created_at", "updated_at"]
