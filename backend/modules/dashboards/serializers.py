from rest_framework import serializers

from api.v1.serializer_fields import TenantScopedSerializerMixin
from modules.dashboards.models import Dashboard, DashboardWidget


class DashboardWidgetSerializer(
    TenantScopedSerializerMixin, serializers.ModelSerializer
):
    class Meta:
        model = DashboardWidget
        fields = [
            "id",
            "dashboard",
            "position",
            "widget_type",
            "title",
            "subtitle",
            "data_source",
            "config_json",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DashboardSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    widgets = DashboardWidgetSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = [
            "id",
            "name",
            "slug",
            "is_default",
            "industry_preset",
            "layout_json",
            "widgets",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "widgets"]
