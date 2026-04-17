from rest_framework import viewsets

from api.v1.filters import CompanyScopedFilterBackend
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


class DriverViewSet(viewsets.ModelViewSet):
    serializer_class = DriverSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Driver.objects.all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Vehicle.objects.select_related("driver").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        driver = self.request.query_params.get("driver")
        if status:
            qs = qs.filter(status=status)
        if driver:
            qs = qs.filter(driver_id=driver)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class MaintenanceLogViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceLogSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = MaintenanceLog.objects.select_related("vehicle").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        vehicle = self.request.query_params.get("vehicle")
        if status:
            qs = qs.filter(status=status)
        if vehicle:
            qs = qs.filter(vehicle_id=vehicle)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class FuelLogViewSet(viewsets.ModelViewSet):
    serializer_class = FuelLogSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = FuelLog.objects.select_related("vehicle").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        vehicle = self.request.query_params.get("vehicle")
        if vehicle:
            qs = qs.filter(vehicle_id=vehicle)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class VehicleServiceViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleServiceSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = VehicleService.objects.select_related("vehicle").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        vehicle = self.request.query_params.get("vehicle")
        if vehicle:
            qs = qs.filter(vehicle_id=vehicle)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
