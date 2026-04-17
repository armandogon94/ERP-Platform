from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.aggregation import AggregationMixin
from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.helpdesk.models import (
    KnowledgeArticle,
    SLAConfig,
    Ticket,
    TicketCategory,
)
from modules.helpdesk.serializers import (
    KnowledgeArticleSerializer,
    SLAConfigSerializer,
    TicketCategorySerializer,
    TicketSerializer,
)


class TicketCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TicketCategorySerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = TicketCategory.objects.all()
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class SLAConfigViewSet(viewsets.ModelViewSet):
    serializer_class = SLAConfigSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = SLAConfig.objects.select_related("category").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        priority = self.request.query_params.get("priority")
        if category:
            qs = qs.filter(category_id=category)
        if priority:
            qs = qs.filter(priority=priority)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class TicketViewSet(AggregationMixin, viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Ticket.objects.select_related(
        "category", "reporter_partner", "reporter_user", "assignee"
    ).all()
    pagination_class = None

    aggregatable_fields = frozenset(
        {"status", "priority", "category", "assignee", "sla_breached"}
    )
    aggregatable_measures = frozenset({"id"})

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        priority = self.request.query_params.get("priority")
        category = self.request.query_params.get("category")
        assignee = self.request.query_params.get("assignee")
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if category:
            qs = qs.filter(category_id=category)
        if assignee:
            qs = qs.filter(assignee_id=assignee)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED):
            return Response(
                {"detail": "Ticket is already resolved or closed."},
                status=400,
            )
        ticket.status = Ticket.Status.RESOLVED
        ticket.resolved_at = timezone.now()
        ticket.save(update_fields=["status", "resolved_at", "updated_at"])
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status not in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED):
            return Response(
                {"detail": "Only resolved or closed tickets can be reopened."},
                status=400,
            )
        ticket.status = Ticket.Status.IN_PROGRESS
        ticket.resolved_at = None
        ticket.save(update_fields=["status", "resolved_at", "updated_at"])
        return Response(self.get_serializer(ticket).data)


class KnowledgeArticleViewSet(viewsets.ModelViewSet):
    serializer_class = KnowledgeArticleSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = KnowledgeArticle.objects.select_related("category").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        published = self.request.query_params.get("published")
        category = self.request.query_params.get("category")
        if published is not None:
            qs = qs.filter(published=(published.lower() == "true"))
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
