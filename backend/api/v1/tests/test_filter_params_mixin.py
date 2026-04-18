"""Tests for FilterParamsMixin (REVIEW I-12)."""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestFilterParamsMixin:
    """Ride on the fleet.DriverViewSet which uses the mixin for ?status=."""

    def test_status_param_filters_drivers(self, api_client):
        from modules.fleet.models import Driver

        company = CompanyFactory()
        user = UserFactory(company=company)
        Driver.objects.create(company=company, name="Active Alice", status="active")
        Driver.objects.create(
            company=company, name="Suspended Sam", status="suspended"
        )
        auth(api_client, user)

        response = api_client.get("/api/v1/fleet/drivers/?status=active")
        assert response.status_code == 200
        names = [d["name"] for d in response.json()]
        assert "Active Alice" in names
        assert "Suspended Sam" not in names

    def test_unknown_param_is_ignored(self, api_client):
        """Mixin should silently skip params not in filter_params declaration."""
        from modules.fleet.models import Driver

        company = CompanyFactory()
        user = UserFactory(company=company)
        Driver.objects.create(company=company, name="A", status="active")
        Driver.objects.create(company=company, name="B", status="active")
        auth(api_client, user)

        response = api_client.get("/api/v1/fleet/drivers/?garbage=value")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_fk_lookup_via_id_suffix(self, api_client):
        """filter_params value `"vehicle_id"` must route `?vehicle=<N>` to
        `.filter(vehicle_id=<N>)`."""
        from modules.fleet.models import FuelLog, Vehicle

        company = CompanyFactory()
        user = UserFactory(company=company)
        v1 = Vehicle.objects.create(
            company=company, make="Ford", model="Transit", year=2020,
            license_plate="AAA-111",
        )
        v2 = Vehicle.objects.create(
            company=company, make="Toyota", model="Camry", year=2021,
            license_plate="BBB-222",
        )
        FuelLog.objects.create(
            company=company, vehicle=v1, liters=10, cost_per_liter="1.5",
            total_cost="15.00",
        )
        FuelLog.objects.create(
            company=company, vehicle=v2, liters=5, cost_per_liter="1.5",
            total_cost="7.50",
        )
        auth(api_client, user)

        response = api_client.get(f"/api/v1/fleet/fuel-logs/?vehicle={v1.id}")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["vehicle"] == v1.id
