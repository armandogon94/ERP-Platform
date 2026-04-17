from django.urls import include, path
from rest_framework.routers import DefaultRouter

from modules.fleet.viewsets import (
    DriverViewSet,
    FuelLogViewSet,
    MaintenanceLogViewSet,
    VehicleServiceViewSet,
    VehicleViewSet,
)

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("drivers", DriverViewSet, basename="driver")
router.register("maintenance-logs", MaintenanceLogViewSet, basename="maintenance-log")
router.register("fuel-logs", FuelLogViewSet, basename="fuel-log")
router.register("services", VehicleServiceViewSet, basename="vehicle-service")

urlpatterns = [path("", include(router.urls))]
