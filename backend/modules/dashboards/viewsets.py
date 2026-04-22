from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.dashboards.data_sources import compute_data_source
from modules.dashboards.models import Dashboard, DashboardWidget
from modules.dashboards.serializers import (
    DashboardSerializer,
    DashboardWidgetSerializer,
)
from modules.dashboards.seed import seed_default_dashboard


class DashboardViewSet(viewsets.ModelViewSet):
    """Per-company dashboards.

    On first GET, if no dashboards exist yet, we lazily seed the industry's
    default from ``industry_presets/*.yaml``. This keeps the UX instant —
    no separate provisioning step.
    """

    serializer_class = DashboardSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Dashboard.objects.prefetch_related("widgets").all()

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def list(self, request, *args, **kwargs):
        # Lazy seed: if the tenant has no dashboard yet, create the default
        # one from its industry preset before responding.
        self._ensure_default(request.company)
        return super().list(request, *args, **kwargs)

    def _ensure_default(self, company):
        if not Dashboard.objects.filter(company=company).exists():
            seed_default_dashboard(company)

    @action(detail=False, methods=["get"])
    def default(self, request):
        """Return the company's default dashboard (seeding on first access)."""
        self._ensure_default(request.company)
        qs = self.filter_queryset(self.get_queryset())
        dashboard = qs.filter(is_default=True).first() or qs.first()
        if not dashboard:
            return Response({"detail": "No default dashboard."}, status=404)
        return Response(self.get_serializer(dashboard).data)

    @action(detail=True, methods=["get"])
    def data(self, request, pk=None):
        """Return the data payload for every widget on this dashboard.

        Returns ``{widget_id: <shape>, ...}`` so the frontend can render
        everything from a single response.
        """
        dashboard = self.get_object()
        out = {}
        for widget in dashboard.widgets.all().order_by("position"):
            try:
                out[widget.id] = compute_data_source(
                    widget.data_source,
                    request.company,
                    widget.config_json or {},
                )
            except KeyError:
                out[widget.id] = {
                    "error": f"Unknown data source: {widget.data_source}",
                }
            except Exception as e:  # noqa: BLE001 — surface but don't crash
                out[widget.id] = {"error": str(e)}
        return Response(out)

    @action(detail=True, methods=["post"])
    def reseed(self, request, pk=None):
        """Wipe widgets and re-seed from the industry preset.

        Useful when a preset has been updated and the user wants to get the
        new defaults. Preserves the Dashboard row (so ID stays stable).
        """
        dashboard = self.get_object()
        dashboard.widgets.all().delete()
        seed_default_dashboard(request.company, target=dashboard)
        dashboard.refresh_from_db()
        return Response(self.get_serializer(dashboard).data)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = DashboardWidget.objects.select_related("dashboard").all()

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    @action(detail=True, methods=["get"])
    def data(self, request, pk=None):
        """Refresh a single widget's data."""
        widget = self.get_object()
        try:
            payload = compute_data_source(
                widget.data_source,
                request.company,
                widget.config_json or {},
            )
            return Response(payload)
        except KeyError:
            return Response(
                {"error": f"Unknown data source: {widget.data_source}"},
                status=400,
            )
