from rest_framework import serializers

from modules.sales.models import SalesOrder, SalesOrderLine, SalesQuotation


class SalesQuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesQuotation
        fields = [
            "id",
            "quotation_number",
            "customer_name",
            "customer_email",
            "status",
            "valid_until",
            "notes",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SalesOrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderLine
        fields = [
            "id",
            "sales_order",
            "description",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SalesOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = [
            "id",
            "order_number",
            "customer_name",
            "customer_email",
            "quotation",
            "status",
            "order_date",
            "delivery_date",
            "notes",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
