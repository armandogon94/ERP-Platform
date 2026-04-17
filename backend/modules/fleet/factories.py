import datetime
from decimal import Decimal

import factory

from core.factories import CompanyFactory
from modules.fleet.models import Driver, FuelLog, MaintenanceLog, Vehicle, VehicleService


class DriverFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Driver
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Driver {n}")
    license_number = factory.Sequence(lambda n: f"DL-{n:05d}")
    license_expiry = factory.LazyFunction(lambda: datetime.date(2030, 1, 1))
    phone = ""
    status = Driver.Status.ACTIVE


class VehicleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vehicle
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    make = "Ford"
    model = "Transit"
    year = 2024
    license_plate = factory.Sequence(lambda n: f"ABC-{n:04d}")
    vin = factory.Sequence(lambda n: f"1FTBW2CM{n:08d}")
    status = Vehicle.Status.ACTIVE
    driver = None
    mileage = 0


class MaintenanceLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceLog
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    vehicle = factory.SubFactory(
        VehicleFactory, company=factory.SelfAttribute("..company")
    )
    date = factory.LazyFunction(lambda: datetime.date(2026, 1, 15))
    description = "Routine inspection"
    cost = Decimal("0.00")
    mechanic = ""
    status = MaintenanceLog.Status.SCHEDULED


class FuelLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FuelLog
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    vehicle = factory.SubFactory(
        VehicleFactory, company=factory.SelfAttribute("..company")
    )
    date = factory.LazyFunction(lambda: datetime.date(2026, 1, 10))
    liters = Decimal("40.00")
    cost_per_liter = Decimal("1.500")
    total_cost = Decimal("60.00")
    mileage_at_fill = 10000


class VehicleServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VehicleService
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    vehicle = factory.SubFactory(
        VehicleFactory, company=factory.SelfAttribute("..company")
    )
    service_type = "Tire rotation"
    scheduled_date = factory.LazyFunction(lambda: datetime.date(2026, 2, 1))
    completed_date = None
    cost = Decimal("0.00")
    notes = ""
