from rest_framework import serializers

from modules.purchasing.models import POLine, PurchaseOrder, RequestForQuote, RFQLine, Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id",
            "name",
            "email",
            "contact_name",
            "phone",
            "address",
            "currency",
            "payment_terms",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class POLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = POLine
        fields = [
            "id",
            "purchase_order",
            "description",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "vendor",
            "vendor_name",
            "partner",
            "po_number",
            "status",
            "order_date",
            "expected_date",
            "notes",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "vendor_name", "created_at", "updated_at"]


class RFQLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQLine
        fields = [
            "id",
            "rfq",
            "description",
            "quantity",
            "unit_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RequestForQuoteSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)

    class Meta:
        model = RequestForQuote
        fields = [
            "id",
            "vendor",
            "vendor_name",
            "rfq_number",
            "status",
            "request_date",
            "deadline",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "vendor_name", "created_at", "updated_at"]
