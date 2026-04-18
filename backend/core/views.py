from django.db.models import Count, Sum
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyAdmin, IsCompanyMember
from core.models import (
    AuditLog,
    ModuleConfig,
    ModuleRegistry,
    Notification,
    Partner,
    ViewDefinition,
)
from core.serializers import (
    AuditLogSerializer,
    ConfigPatchSerializer,
    ModuleSerializer,
    NotificationSerializer,
    PartnerSerializer,
    ResolvedConfigSerializer,
    ViewDefinitionSerializer,
)
from core.services.config_service import (
    get_resolved_config,
    get_terminology,
    invalidate_company_config,
    merge_configs,
)


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """List installed modules for the authenticated user's company."""

    serializer_class = ModuleSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ModuleRegistry.objects.order_by("sequence", "name")

    @action(detail=True, methods=["get", "patch"])
    def config(self, request, pk=None):
        if request.method == "PATCH":
            return self._patch_config(request, pk)
        return self._get_config(request, pk)

    def _get_config(self, request, pk):
        module = self.get_object()
        config = get_resolved_config(request.company, module_name=module.name)
        terminology = config.get("terminology", {})
        serializer = ResolvedConfigSerializer(
            {
                "module": module.name,
                "industry": request.company.industry,
                "config": config,
                "terminology": terminology,
            }
        )
        return Response(serializer.data)

    def _patch_config(self, request, pk):
        # REVIEW I-3: check admin via the standard DRF permission machinery
        # so it short-circuits before body parsing and returns a consistent
        # 403 shape.
        admin_perm = IsCompanyAdmin()
        if not admin_perm.has_permission(request, self):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only company admins can update module config.")

        module = self.get_object()
        patch_serializer = ConfigPatchSerializer(data=request.data)
        patch_serializer.is_valid(raise_exception=True)

        overrides = patch_serializer.validated_data["overrides"]

        # Merge overrides into Company.config_json and save
        company = request.company
        current_config = company.config_json or {}
        company.config_json = merge_configs(current_config, overrides)
        company.save(update_fields=["config_json", "updated_at"])

        # Invalidate cache (signal also fires, but we invalidate explicitly here too)
        invalidate_company_config(company.id)

        # Return updated resolved config
        config = get_resolved_config(company, module_name=module.name)
        terminology = config.get("terminology", {})
        serializer = ResolvedConfigSerializer(
            {
                "module": module.name,
                "industry": company.industry,
                "config": config,
                "terminology": terminology,
            }
        )
        return Response(serializer.data)


class ViewDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve view definitions for the authenticated user's company."""

    serializer_class = ViewDefinitionSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ViewDefinition.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        model_name = self.request.query_params.get("model_name")
        view_type = self.request.query_params.get("view_type")
        if model_name:
            qs = qs.filter(model_name=model_name)
        if view_type:
            qs = qs.filter(view_type=view_type)
        return qs

    @action(detail=False, methods=["get"])
    def default(self, request):
        model_name = request.query_params.get("model_name")
        view_type = request.query_params.get("view_type")
        if not model_name or not view_type:
            return Response(
                {"detail": "model_name and view_type are required"},
                status=400,
            )
        qs = self.filter_queryset(self.get_queryset())
        view = qs.filter(
            model_name=model_name, view_type=view_type, is_default=True,
        ).first()
        if not view:
            return Response({"detail": "No default view found"}, status=404)
        serializer = self.get_serializer(view)
        return Response(serializer.data)


class PartnerViewSet(viewsets.ModelViewSet):
    """CRUD for company-scoped Partner records (Slice 10.6, D21).

    REVIEW C-2: destructive operations (create/update/destroy) require
    company-admin privileges; reads remain open to any company member.
    Partners cascade into invoices, sales orders, tickets, and projects,
    so allowing any member to delete them was a privilege-escalation path.
    """

    serializer_class = PartnerSerializer
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Partner.objects.all()

    def get_permissions(self):
        # Read-only actions only need company membership.
        if self.action in {"list", "retrieve"}:
            return [IsCompanyMember()]
        return [IsCompanyMember(), IsCompanyAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        is_customer = self.request.query_params.get("is_customer")
        is_vendor = self.request.query_params.get("is_vendor")
        if is_customer is not None:
            qs = qs.filter(is_customer=(is_customer.lower() == "true"))
        if is_vendor is not None:
            qs = qs.filter(is_vendor=(is_vendor.lower() == "true"))
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only company-scoped audit log (Slice 19)."""

    serializer_class = AuditLogSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = AuditLog.objects.select_related("user").order_by("-timestamp")

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())[:100]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """User-scoped notifications (list, mark-read, unread-count) (Slice 19)."""

    serializer_class = NotificationSerializer
    permission_classes = [IsCompanyMember]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        # REVIEW I-9: emit the unread count as a response header so the
        # frontend bell can refresh both fields in a single round-trip
        # instead of polling /unread_count/ separately every 30s. Response
        # body remains a plain array for backward compat with existing
        # TypeScript clients.
        qs = self.get_queryset()[:50]
        unread = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        serializer = self.get_serializer(qs, many=True)
        return Response(
            serializer.data,
            headers={"X-Unread-Count": str(unread)},
        )

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        n = Notification.objects.filter(
            recipient=request.user, pk=pk
        ).first()
        if not n:
            return Response({"detail": "Not found"}, status=404)
        n.is_read = True
        n.save(update_fields=["is_read"])
        return Response(self.get_serializer(n).data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({"count": count})


# REVIEW S-2: KPI tile definitions are table-driven so adding a tile is
# a 1-line change. Each entry is (module_path, model_class_name, label,
# tile_fn) where tile_fn receives a company-scoped queryset and returns
# a dict with at least "value"; "detail" is optional.
_HOME_KPI_DEFS = [
    (
        "modules.invoicing.models", "Invoice", "Outstanding Invoices", "invoicing",
        lambda qs: (
            lambda agg: {
                "value": f"{agg['count'] or 0}",
                "detail": f"${agg['total'] or 0:.2f}",
            }
        )(qs.filter(status="posted").aggregate(total=Sum("total_amount"), count=Count("id"))),
    ),
    (
        "modules.sales.models", "SalesOrder", "Open Sales Orders", "sales",
        lambda qs: {"value": str(qs.filter(status__in=["confirmed", "in_progress"]).count())},
    ),
    (
        "modules.purchasing.models", "PurchaseOrder", "Open Purchase Orders", "purchasing",
        lambda qs: {"value": str(qs.filter(status__in=["draft", "sent", "confirmed"]).count())},
    ),
    (
        "modules.helpdesk.models", "Ticket", "Open Tickets", "helpdesk",
        lambda qs: {"value": str(qs.exclude(status__in=["resolved", "closed"]).count())},
    ),
    (
        "modules.hr.models", "Employee", "Active Employees", "hr",
        lambda qs: {"value": str(qs.count())},
    ),
    (
        "modules.inventory.models", "Product", "Products in Catalog", "inventory",
        lambda qs: {"value": str(qs.count())},
    ),
]


def _compute_home_kpis(company):
    """Walk _HOME_KPI_DEFS and assemble the tile list for one company."""
    from importlib import import_module

    tiles: list[dict] = []
    for module_path, class_name, label, module_tag, tile_fn in _HOME_KPI_DEFS:
        try:
            module = import_module(module_path)
            model_cls = getattr(module, class_name)
            qs = model_cls.objects.filter(company=company)
            tile = {"label": label, "module": module_tag, **tile_fn(qs)}
            tiles.append(tile)
        except (ImportError, LookupError, AttributeError):
            # REVIEW I-6: module not installed → skip. Narrow exception
            # list so real ORM bugs still surface.
            continue
    return tiles


@api_view(["GET"])
@permission_classes([IsCompanyMember])
def home_kpis(request):
    """Lightweight home KPIs using plain ORM aggregates (no materialized views, D25).

    REVIEW S-1: cached for 60 seconds per company to cut DB load on
    dashboard refreshes. REVIEW S-2: tile definitions are table-driven
    in ``_HOME_KPI_DEFS`` so adding a new tile is one list entry.
    """
    from django.core.cache import cache

    company = request.company
    cache_key = f"home_kpis:{company.id}"
    tiles = cache.get(cache_key)
    if tiles is None:
        tiles = _compute_home_kpis(company)
        cache.set(cache_key, tiles, timeout=60)

    return Response({"tiles": tiles})
