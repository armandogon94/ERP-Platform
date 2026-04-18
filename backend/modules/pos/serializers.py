from rest_framework import serializers

from modules.pos.models import CashMovement, POSOrder, POSOrderLine, POSSession
from api.v1.serializer_fields import TenantScopedSerializerMixin


class POSSessionSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    opened_by_username = serializers.CharField(
        source="opened_by.username", read_only=True
    )

    class Meta:
        model = POSSession
        fields = [
            "id",
            "station",
            "cash_on_open",
            "cash_on_close",
            "expected_cash",
            "variance",
            "opened_by",
            "opened_by_username",
            "opened_at",
            "closed_at",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "opened_by",
            "opened_by_username",
            "opened_at",
            "expected_cash",
            "variance",
            "created_at",
            "updated_at",
        ]


class POSOrderLineSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = POSOrderLine
        fields = [
            "id",
            "order",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "tax_rate",
            "total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "product_name", "created_at", "updated_at"]


class POSOrderSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = POSOrder
        fields = [
            "id",
            "session",
            "order_number",
            "customer",
            "customer_name",
            "subtotal",
            "tax_amount",
            "total",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "order_number",
            "customer_name",
            "created_at",
            "updated_at",
        ]


class CashMovementSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CashMovement
        fields = [
            "id",
            "session",
            "type",
            "amount",
            "reason",
            "at_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "at_time", "created_at", "updated_at"]


class SessionCloseSerializer(serializers.Serializer):
    cash_on_close = serializers.DecimalField(max_digits=12, decimal_places=2)
