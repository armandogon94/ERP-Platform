from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from core.models import ModuleConfig, ModuleRegistry
from core.serializers import ModuleConfigSerializer, ModuleSerializer


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
