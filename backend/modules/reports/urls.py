from django.urls import include, path
from rest_framework.routers import DefaultRouter

from modules.reports.viewsets import (
    PivotDefinitionViewSet,
    ReportTemplateViewSet,
    ScheduledExportViewSet,
)

router = DefaultRouter()
router.register("templates", ReportTemplateViewSet, basename="report-template")
router.register("pivots", PivotDefinitionViewSet, basename="pivot-definition")
router.register("schedules", ScheduledExportViewSet, basename="scheduled-export")

urlpatterns = [path("", include(router.urls))]
