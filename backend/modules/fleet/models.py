"""Fleet module models: Vehicle, Driver, MaintenanceLog, FuelLog, VehicleService."""

from django.db import models

from core.models import TenantModel


class Driver(TenantModel):
    """A person authorized to drive company vehicles."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, blank=True, default="")
    license_expiry = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=40, blank=True, default="")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    employee = models.ForeignKey(
        "hr.Employee",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta(TenantModel.Meta):
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Vehicle(TenantModel):
    """A fleet vehicle."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        MAINTENANCE = "maintenance", "In Maintenance"
        RETIRED = "retired", "Retired"

    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=50)
    vin = models.CharField(max_length=50, blank=True, default="")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    driver = models.ForeignKey(
        Driver,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="vehicles",
    )
    mileage = models.PositiveIntegerField(default=0)

    class Meta(TenantModel.Meta):
        ordering = ["license_plate"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "license_plate"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_vehicle_plate_per_company",
            ),
        ]

    def __str__(self) -> str:
        return self.license_plate


class MaintenanceLog(TenantModel):
    """A scheduled or completed maintenance event for a vehicle."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="maintenance_logs"
    )
    date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mechanic = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )

    class Meta(TenantModel.Meta):
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.vehicle.license_plate} — {self.description[:40] or self.status}"


class FuelLog(TenantModel):
    """A single fuel fill-up for a vehicle."""

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="fuel_logs"
    )
    date = models.DateField(null=True, blank=True)
    liters = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    cost_per_liter = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mileage_at_fill = models.PositiveIntegerField(default=0)

    class Meta(TenantModel.Meta):
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.vehicle.license_plate} @ {self.date}"


class VehicleService(TenantModel):
    """A planned or completed service appointment (tires, inspection, etc.)."""

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="services"
    )
    service_type = models.CharField(max_length=100)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["-scheduled_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.vehicle.license_plate} — {self.service_type}"
