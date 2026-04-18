from rest_framework import serializers

from modules.manufacturing.models import (
    BillOfMaterials,
    BOMLine,
    ProductionCost,
    WorkOrder,
)
from api.v1.serializer_fields import TenantScopedSerializerMixin


class BillOfMaterialsSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = BillOfMaterials
        fields = [
            "id",
            "product",
            "product_name",
            "version",
            "active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "product_name", "created_at", "updated_at"]


class BOMLineSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    component_name = serializers.CharField(source="component.name", read_only=True)

    class Meta:
        model = BOMLine
        fields = [
            "id",
            "bom",
            "component",
            "component_name",
            "quantity",
            "uom",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "component_name", "created_at", "updated_at"]


class WorkOrderSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "product",
            "product_name",
            "bom",
            "quantity_target",
            "quantity_done",
            "status",
            "start_date",
            "end_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "product_name", "created_at", "updated_at"]


class ProductionCostSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductionCost
        fields = [
            "id",
            "work_order",
            "cost_type",
            "amount",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
