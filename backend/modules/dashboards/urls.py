from django.urls import include, path
from rest_framework.routers import DefaultRouter

from modules.dashboards.viewsets import DashboardViewSet, DashboardWidgetViewSet

router = DefaultRouter()
router.register("dashboards", DashboardViewSet, basename="dashboard")
router.register("widgets", DashboardWidgetViewSet, basename="dashboard-widget")

urlpatterns = [path("", include(router.urls))]
