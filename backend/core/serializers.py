from django.contrib.auth.models import User
from rest_framework import serializers

from core.models import Company, ModuleConfig, ModuleRegistry, ViewDefinition


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "slug", "brand_color", "industry"]


class UserSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "company"]

    def get_company(self, obj):
        if hasattr(obj, "profile"):
            return CompanySerializer(obj.profile.company).data
        return None


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleRegistry
        fields = [
            "id", "name", "display_name", "icon",
            "is_installed", "is_visible", "sequence", "color",
        ]


class ModuleConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleConfig
        fields = ["id", "key", "value", "value_type"]


class ResolvedConfigSerializer(serializers.Serializer):
    """Serializer for the resolved 3-tier config response."""

    module = serializers.CharField()
    industry = serializers.CharField()
    config = serializers.DictField()
    terminology = serializers.DictField()


class ConfigPatchSerializer(serializers.Serializer):
    """Validates the PATCH body for module config overrides."""

    overrides = serializers.DictField(
        child=serializers.JSONField(),
        help_text="Partial config dict to merge into Company.config_json.",
    )


class ViewDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewDefinition
        fields = [
            "id", "model_name", "view_type", "name",
            "is_default", "priority", "config",
        ]
