from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import (
    AuditLogViewSet,
    ModuleViewSet,
    NotificationViewSet,
    PartnerViewSet,
    ViewDefinitionViewSet,
    home_kpis,
)

router = DefaultRouter()
router.register("modules", ModuleViewSet, basename="module")
router.register("views", ViewDefinitionViewSet, basename="viewdefinition")
router.register("partners", PartnerViewSet, basename="partner")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("audit-logs", AuditLogViewSet, basename="auditlog")

urlpatterns = [
    path("home-kpis/", home_kpis, name="home-kpis"),
    path("", include(router.urls)),
]
