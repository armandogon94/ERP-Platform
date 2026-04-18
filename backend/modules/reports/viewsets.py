from rest_framework import viewsets

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.reports.models import PivotDefinition, ReportTemplate, ScheduledExport
from modules.reports.serializers import (
    PivotDefinitionSerializer,
    ReportTemplateSerializer,
    ScheduledExportSerializer,
)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ReportTemplate.objects.all()

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class PivotDefinitionViewSet(viewsets.ModelViewSet):
    serializer_class = PivotDefinitionSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = PivotDefinition.objects.all()

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class ScheduledExportViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledExportSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ScheduledExport.objects.select_related("report").all()

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
