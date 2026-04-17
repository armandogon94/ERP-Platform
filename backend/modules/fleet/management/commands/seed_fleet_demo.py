import datetime

from core.management.commands._seed_helpers import SeedCommandBase
from modules.fleet.models import Driver, Vehicle


class Command(SeedCommandBase):
    help = "Seed demo drivers + vehicles for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            Vehicle.objects.filter(company=company).delete()
            Driver.objects.filter(company=company).delete()

        driver, _ = Driver.objects.get_or_create(
            company=company,
            license_number="DEMO-DL-001",
            defaults={
                "name": "Demo Driver",
                "license_expiry": datetime.date(2030, 1, 1),
                "status": "active",
            },
        )
        vehicle_specs = [
            ("DEMO-V-1", "Ford", "Transit", 2024),
            ("DEMO-V-2", "Mercedes", "Sprinter", 2023),
        ]
        for plate, make, model, year in vehicle_specs:
            Vehicle.objects.get_or_create(
                company=company,
                license_plate=plate,
                defaults={
                    "make": make,
                    "model": model,
                    "year": year,
                    "driver": driver,
                    "status": "active",
                },
            )
        return 1 + len(vehicle_specs)
