"""Tests for the Partner REST API at /api/v1/core/partners/ (Slice 10.6)."""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, PartnerFactory, UserFactory


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestPartnerAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/core/partners/")
        assert response.status_code == 401

    def test_list_returns_company_partners(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        PartnerFactory(company=company, name="Acme Corp")
        PartnerFactory(company=company, name="Globex Inc")
        auth(api_client, user)

        response = api_client.get("/api/v1/core/partners/")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert "Acme Corp" in names
        assert "Globex Inc" in names

    def test_list_filters_by_is_customer(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        PartnerFactory(company=company, name="Customer Only", is_customer=True, is_vendor=False)
        PartnerFactory(company=company, name="Vendor Only", is_customer=False, is_vendor=True)
        auth(api_client, user)

        response = api_client.get("/api/v1/core/partners/?is_customer=true")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert "Customer Only" in names
        assert "Vendor Only" not in names

    def test_list_filters_by_is_vendor(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        PartnerFactory(company=company, name="Customer Only", is_customer=True, is_vendor=False)
        PartnerFactory(company=company, name="Vendor Only", is_customer=False, is_vendor=True)
        auth(api_client, user)

        response = api_client.get("/api/v1/core/partners/?is_vendor=true")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert "Vendor Only" in names
        assert "Customer Only" not in names

    def test_retrieve_returns_partner(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        partner = PartnerFactory(company=company, name="Detail Partner")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/core/partners/{partner.pk}/")
        assert response.status_code == 200
        assert response.json()["name"] == "Detail Partner"

    def test_create_partner(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        payload = {
            "name": "New Partner",
            "email": "new@example.com",
            "is_customer": True,
            "is_vendor": False,
        }
        response = api_client.post(
            "/api/v1/core/partners/", payload, format="json"
        )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "New Partner"
        assert body["is_customer"] is True

    def test_create_does_not_require_company_field(self, api_client):
        """perform_create should inject request.company — client should not pass it."""
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/core/partners/",
            {"name": "No Company Field"},
            format="json",
        )
        assert response.status_code == 201

    def test_update_partner(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        partner = PartnerFactory(company=company, name="Original Name")
        auth(api_client, user)

        response = api_client.patch(
            f"/api/v1/core/partners/{partner.pk}/",
            {"name": "Updated Name"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_delete_partner(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        partner = PartnerFactory(company=company, name="Delete Me")
        auth(api_client, user)

        response = api_client.delete(f"/api/v1/core/partners/{partner.pk}/")
        assert response.status_code == 204

    def test_cross_company_retrieve_returns_404(self, api_client):
        company_a = CompanyFactory(slug="co-a")
        company_b = CompanyFactory(slug="co-b")
        user_a = UserFactory(company=company_a)
        partner_b = PartnerFactory(company=company_b, name="B Secret Partner")
        auth(api_client, user_a)

        response = api_client.get(f"/api/v1/core/partners/{partner_b.pk}/")
        assert response.status_code == 404

    def test_cross_company_list_excludes_other_company(self, api_client):
        company_a = CompanyFactory(slug="co-a")
        company_b = CompanyFactory(slug="co-b")
        user_a = UserFactory(company=company_a)
        PartnerFactory(company=company_a, name="A Partner")
        PartnerFactory(company=company_b, name="B Secret Partner")
        auth(api_client, user_a)

        response = api_client.get("/api/v1/core/partners/")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert "A Partner" in names
        assert "B Secret Partner" not in names
