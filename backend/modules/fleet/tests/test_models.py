"""Model tests for the Fleet module (Slice 11)."""

import datetime
from decimal import Decimal

import pytest

from core.factories import CompanyFactory
from modules.fleet.factories import (
    DriverFactory,
    FuelLogFactory,
    MaintenanceLogFactory,
    VehicleFactory,
    VehicleServiceFactory,
)
from modules.fleet.models import (
    Driver,
    FuelLog,
    MaintenanceLog,
    Vehicle,
    VehicleService,
)


@pytest.mark.django_db
class TestVehicle:
    def test_create_vehicle(self):
        v = VehicleFactory()
        assert v.pk is not None
        assert v.license_plate.startswith("ABC-")
        assert v.status == Vehicle.Status.ACTIVE

    def test_str_returns_plate(self):
        v = VehicleFactory(license_plate="XYZ-999")
        assert str(v) == "XYZ-999"

    def test_company_isolation(self):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        VehicleFactory(company=a, license_plate="A-1")
        VehicleFactory(company=b, license_plate="B-1")
        assert Vehicle.objects.filter(company=a).count() == 1
        assert Vehicle.objects.filter(company=b).count() == 1

    def test_driver_nullable(self):
        v = VehicleFactory(driver=None)
        assert v.driver is None

    def test_assigned_driver_from_same_company(self):
        company = CompanyFactory()
        driver = DriverFactory(company=company)
        v = VehicleFactory(company=company, driver=driver)
        assert v.driver_id == driver.id


@pytest.mark.django_db
class TestDriver:
    def test_create_driver(self):
        d = DriverFactory()
        assert d.pk is not None
        assert d.status == Driver.Status.ACTIVE

    def test_str_returns_name(self):
        d = DriverFactory(name="Jane Smith")
        assert str(d) == "Jane Smith"

    def test_license_expiry_future(self):
        d = DriverFactory(license_expiry=datetime.date(2030, 1, 1))
        assert d.license_expiry == datetime.date(2030, 1, 1)


@pytest.mark.django_db
class TestMaintenanceLog:
    def test_create_maintenance_log(self):
        log = MaintenanceLogFactory()
        assert log.pk is not None
        assert log.status == MaintenanceLog.Status.SCHEDULED

    def test_str_includes_vehicle_plate(self):
        company = CompanyFactory()
        v = VehicleFactory(company=company, license_plate="MNT-1")
        log = MaintenanceLogFactory(
            company=company,
            vehicle=v,
            description="Oil change",
        )
        s = str(log)
        assert "MNT-1" in s

    def test_cost_precision(self):
        log = MaintenanceLogFactory(cost=Decimal("125.50"))
        assert log.cost == Decimal("125.50")


@pytest.mark.django_db
class TestFuelLog:
    def test_create_fuel_log(self):
        log = FuelLogFactory()
        assert log.pk is not None
        assert log.liters > 0

    def test_total_cost_decimal(self):
        log = FuelLogFactory(
            liters=Decimal("40.0"),
            cost_per_liter=Decimal("1.50"),
            total_cost=Decimal("60.00"),
        )
        assert log.total_cost == Decimal("60.00")


@pytest.mark.django_db
class TestVehicleService:
    def test_create_service(self):
        s = VehicleServiceFactory()
        assert s.pk is not None
        assert s.service_type  # non-empty

    def test_completed_date_optional(self):
        s = VehicleServiceFactory(completed_date=None)
        assert s.completed_date is None
