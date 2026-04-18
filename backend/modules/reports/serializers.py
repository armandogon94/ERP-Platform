from rest_framework import serializers

from modules.reports.models import PivotDefinition, ReportTemplate, ScheduledExport
from api.v1.serializer_fields import TenantScopedSerializerMixin


class ReportTemplateSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = [
            "id",
            "name",
            "model_name",
            "default_filters",
            "default_group_by",
            "default_measures",
            "industry_tag",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PivotDefinitionSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PivotDefinition
        fields = [
            "id",
            "name",
            "model_name",
            "rows",
            "cols",
            "measure",
            "aggregator",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ScheduledExportSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ScheduledExport
        fields = [
            "id",
            "report",
            "cron",
            "format",
            "recipients",
            "last_run",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_run", "created_at", "updated_at"]
