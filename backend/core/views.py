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
    pagination_class = None

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
        # Require company admin
        if not request.is_company_admin:
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
    pagination_class = None

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
    pagination_class = None

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
    pagination_class = None

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())[:100]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """User-scoped notifications (list, mark-read, unread-count) (Slice 19)."""

    serializer_class = NotificationSerializer
    permission_classes = [IsCompanyMember]
    pagination_class = None

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()[:50]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

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


@api_view(["GET"])
@permission_classes([IsCompanyMember])
def home_kpis(request):
    """Lightweight home KPIs using plain ORM aggregates (no materialized views, D25).

    Returns 4-6 tiles summarising the authenticated user's company. Modules
    that aren't installed return a zero/absent tile rather than a crash.
    """
    company = request.company
    tiles: list[dict] = []

    # Invoicing — outstanding invoices (posted but not paid)
    try:
        from modules.invoicing.models import Invoice

        outstanding = Invoice.objects.filter(
            company=company, status="posted"
        ).aggregate(total=Sum("total_amount"), count=Count("id"))
        tiles.append({
            "label": "Outstanding Invoices",
            "value": f"{outstanding['count'] or 0}",
            "detail": f"${outstanding['total'] or 0:.2f}",
            "module": "invoicing",
        })
    except Exception:
        pass

    # Sales — open sales orders (REVIEW C-5: SalesOrder has no "draft" state;
    # real open statuses are "confirmed" and "in_progress").
    try:
        from modules.sales.models import SalesOrder

        open_orders = SalesOrder.objects.filter(
            company=company, status__in=["confirmed", "in_progress"]
        ).count()
        tiles.append({
            "label": "Open Sales Orders",
            "value": str(open_orders),
            "module": "sales",
        })
    except Exception:
        pass

    # Purchasing — open POs
    try:
        from modules.purchasing.models import PurchaseOrder

        open_pos = PurchaseOrder.objects.filter(
            company=company, status__in=["draft", "sent", "confirmed"]
        ).count()
        tiles.append({
            "label": "Open Purchase Orders",
            "value": str(open_pos),
            "module": "purchasing",
        })
    except Exception:
        pass

    # Helpdesk — open tickets
    try:
        from modules.helpdesk.models import Ticket

        open_tickets = Ticket.objects.filter(
            company=company
        ).exclude(status__in=["resolved", "closed"]).count()
        tiles.append({
            "label": "Open Tickets",
            "value": str(open_tickets),
            "module": "helpdesk",
        })
    except Exception:
        pass

    # HR — active employees
    try:
        from modules.hr.models import Employee

        employees = Employee.objects.filter(company=company).count()
        tiles.append({
            "label": "Active Employees",
            "value": str(employees),
            "module": "hr",
        })
    except Exception:
        pass

    # Inventory — products below reorder threshold
    try:
        from modules.inventory.models import Product

        products = Product.objects.filter(company=company).count()
        tiles.append({
            "label": "Products in Catalog",
            "value": str(products),
            "module": "inventory",
        })
    except Exception:
        pass

    return Response({"tiles": tiles})
