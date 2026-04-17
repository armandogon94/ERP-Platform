from rest_framework import serializers

from modules.helpdesk.models import (
    KnowledgeArticle,
    SLAConfig,
    Ticket,
    TicketCategory,
)


class TicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory
        fields = [
            "id",
            "name",
            "sla_hours",
            "industry_tag",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SLAConfigSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = SLAConfig
        fields = [
            "id",
            "category",
            "category_name",
            "priority",
            "response_hours",
            "resolution_hours",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "category_name", "created_at", "updated_at"]


class TicketSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    reporter_partner_name = serializers.CharField(
        source="reporter_partner.name", read_only=True
    )
    assignee_username = serializers.CharField(
        source="assignee.username", read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "title",
            "description",
            "category",
            "category_name",
            "reporter_partner",
            "reporter_partner_name",
            "reporter_user",
            "assignee",
            "assignee_username",
            "priority",
            "status",
            "resolved_at",
            "sla_breached",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "ticket_number",
            "category_name",
            "reporter_partner_name",
            "assignee_username",
            "resolved_at",
            "created_at",
            "updated_at",
        ]


class KnowledgeArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = KnowledgeArticle
        fields = [
            "id",
            "title",
            "slug",
            "body",
            "category",
            "category_name",
            "published",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "category_name", "created_at", "updated_at"]
