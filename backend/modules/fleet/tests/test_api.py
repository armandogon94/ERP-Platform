"""API tests for the Fleet module."""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.fleet.factories import (
    DriverFactory,
    FuelLogFactory,
    MaintenanceLogFactory,
    VehicleFactory,
    VehicleServiceFactory,
)
from modules.fleet.models import Driver, Vehicle


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestVehicleAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/fleet/vehicles/")
        assert response.status_code == 401

    def test_list_scopes_to_company(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        VehicleFactory(company=company, license_plate="CUR-1")
        VehicleFactory(license_plate="OTHER-1")  # different company
        auth(api_client, user)

        response = api_client.get("/api/v1/fleet/vehicles/")
        assert response.status_code == 200
        plates = [v["license_plate"] for v in response.json()]
        assert "CUR-1" in plates
        assert "OTHER-1" not in plates

    def test_create_vehicle(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        payload = {
            "make": "Ford",
            "model": "Transit",
            "year": 2024,
            "license_plate": "NEW-1",
            "status": "active",
            "mileage": 0,
        }
        response = api_client.post("/api/v1/fleet/vehicles/", payload, format="json")
        assert response.status_code == 201, response.content
        assert response.json()["license_plate"] == "NEW-1"

    def test_filter_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        VehicleFactory(company=company, license_plate="ACT-1", status="active")
        VehicleFactory(company=company, license_plate="RET-1", status="retired")
        auth(api_client, user)

        response = api_client.get("/api/v1/fleet/vehicles/?status=retired")
        assert response.status_code == 200
        plates = [v["license_plate"] for v in response.json()]
        assert "RET-1" in plates
        assert "ACT-1" not in plates

    def test_filter_by_driver(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        driver = DriverFactory(company=company, name="Alice")
        VehicleFactory(company=company, license_plate="A-1", driver=driver)
        VehicleFactory(company=company, license_plate="N-1", driver=None)
        auth(api_client, user)

        response = api_client.get(f"/api/v1/fleet/vehicles/?driver={driver.id}")
        assert response.status_code == 200
        plates = [v["license_plate"] for v in response.json()]
        assert plates == ["A-1"]

    def test_retrieve_and_delete(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        v = VehicleFactory(company=company)
        auth(api_client, user)

        assert api_client.get(f"/api/v1/fleet/vehicles/{v.pk}/").status_code == 200
        assert api_client.delete(f"/api/v1/fleet/vehicles/{v.pk}/").status_code == 204

    def test_cross_company_404(self, api_client):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        user_a = UserFactory(company=a)
        v_b = VehicleFactory(company=b)
        auth(api_client, user_a)
        assert api_client.get(f"/api/v1/fleet/vehicles/{v_b.pk}/").status_code == 404


@pytest.mark.django_db
class TestDriverAPI:
    def test_list_and_create(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/fleet/drivers/",
            {"name": "Bob", "license_number": "DL-9", "status": "active"},
            format="json",
        )
        assert response.status_code == 201, response.content
        assert Driver.objects.filter(company=company, name="Bob").exists()


@pytest.mark.django_db
class TestMaintenanceLogAPI:
    def test_filter_by_status_and_vehicle(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        v1 = VehicleFactory(company=company, license_plate="V1")
        v2 = VehicleFactory(company=company, license_plate="V2")
        MaintenanceLogFactory(company=company, vehicle=v1, status="scheduled")
        MaintenanceLogFactory(company=company, vehicle=v2, status="completed")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/fleet/maintenance-logs/?vehicle={v2.id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = api_client.get("/api/v1/fleet/maintenance-logs/?status=completed")
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.django_db
class TestFuelLogAPI:
    def test_filter_by_vehicle(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        v1 = VehicleFactory(company=company, license_plate="V1")
        v2 = VehicleFactory(company=company, license_plate="V2")
        FuelLogFactory(company=company, vehicle=v1)
        FuelLogFactory(company=company, vehicle=v2)
        auth(api_client, user)

        response = api_client.get(f"/api/v1/fleet/fuel-logs/?vehicle={v1.id}")
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.django_db
class TestVehicleServiceAPI:
    def test_list_company_scoped(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        VehicleServiceFactory(company=company)
        VehicleServiceFactory()  # other company
        auth(api_client, user)

        response = api_client.get("/api/v1/fleet/services/")
        assert response.status_code == 200
        assert len(response.json()) == 1
