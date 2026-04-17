from rest_framework import serializers

from modules.fleet.models import (
    Driver,
    FuelLog,
    MaintenanceLog,
    Vehicle,
    VehicleService,
)


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            "id",
            "name",
            "license_number",
            "license_expiry",
            "phone",
            "status",
            "employee",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source="driver.name", read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "make",
            "model",
            "year",
            "license_plate",
            "vin",
            "status",
            "driver",
            "driver_name",
            "mileage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "driver_name", "created_at", "updated_at"]


class MaintenanceLogSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(
        source="vehicle.license_plate", read_only=True
    )

    class Meta:
        model = MaintenanceLog
        fields = [
            "id",
            "vehicle",
            "vehicle_plate",
            "date",
            "description",
            "cost",
            "mechanic",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "vehicle_plate", "created_at", "updated_at"]


class FuelLogSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(
        source="vehicle.license_plate", read_only=True
    )

    class Meta:
        model = FuelLog
        fields = [
            "id",
            "vehicle",
            "vehicle_plate",
            "date",
            "liters",
            "cost_per_liter",
            "total_cost",
            "mileage_at_fill",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "vehicle_plate", "created_at", "updated_at"]


class VehicleServiceSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(
        source="vehicle.license_plate", read_only=True
    )

    class Meta:
        model = VehicleService
        fields = [
            "id",
            "vehicle",
            "vehicle_plate",
            "service_type",
            "scheduled_date",
            "completed_date",
            "cost",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "vehicle_plate", "created_at", "updated_at"]
