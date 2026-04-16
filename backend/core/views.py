from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyAdmin, IsCompanyMember
from core.models import ModuleConfig, ModuleRegistry, Partner, ViewDefinition
from core.serializers import (
    ConfigPatchSerializer,
    ModuleSerializer,
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
    """CRUD for company-scoped Partner records (Slice 10.6, D21)."""

    serializer_class = PartnerSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Partner.objects.all()
    pagination_class = None

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
