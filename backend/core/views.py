from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from core.models import ModuleConfig, ModuleRegistry, ViewDefinition
from core.serializers import ModuleConfigSerializer, ModuleSerializer, ViewDefinitionSerializer


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """List installed modules for the authenticated user's company."""

    serializer_class = ModuleSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ModuleRegistry.objects.order_by("sequence", "name")
    pagination_class = None

    @action(detail=True, methods=["get"])
    def config(self, request, pk=None):
        module = self.get_object()
        configs = ModuleConfig.objects.filter(
            company=request.company,
            module=module,
            deleted_at__isnull=True,
        )
        serializer = ModuleConfigSerializer(configs, many=True)
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
