from rest_framework import viewsets

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.mixins import FilterParamsMixin
from api.v1.permissions import IsCompanyMember
from modules.fleet.models import (
    Driver,
    FuelLog,
    MaintenanceLog,
    Vehicle,
    VehicleService,
)
from modules.fleet.serializers import (
    DriverSerializer,
    FuelLogSerializer,
    MaintenanceLogSerializer,
    VehicleSerializer,
    VehicleServiceSerializer,
)


class DriverViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = DriverSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Driver.objects.all()
    filter_params = {"status": "status"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class VehicleViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Vehicle.objects.select_related("driver").all()
    filter_params = {"status": "status", "driver": "driver_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class MaintenanceLogViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = MaintenanceLogSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = MaintenanceLog.objects.select_related("vehicle").all()
    filter_params = {"status": "status", "vehicle": "vehicle_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class FuelLogViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = FuelLogSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = FuelLog.objects.select_related("vehicle").all()
    filter_params = {"vehicle": "vehicle_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class VehicleServiceViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = VehicleServiceSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = VehicleService.objects.select_related("vehicle").all()
    filter_params = {"vehicle": "vehicle_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
