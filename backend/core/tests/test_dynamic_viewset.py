"""Tests for DynamicModelViewSet base class.

Uses ModuleRegistry as a concrete model to test generic CRUD,
filtering, ordering, and search capabilities.
"""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from core.models import ModuleRegistry


@pytest.mark.django_db
class TestDynamicViewSetCRUD:
    def _auth(self, api_client, company):
        user = UserFactory(company=company)
        token = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        return user

    def test_list_returns_company_records(self, api_client):
        company = CompanyFactory()
        self._auth(api_client, company)
        ModuleRegistry.objects.create(
            company=company, name="hr", display_name="HR",
        )
        response = api_client.get("/api/v1/core/modules/")
        assert response.status_code == 200

    def test_retrieve_single_record(self, api_client):
        company = CompanyFactory()
        self._auth(api_client, company)
        mod = ModuleRegistry.objects.create(
            company=company, name="hr", display_name="HR",
        )
        response = api_client.get(f"/api/v1/core/modules/{mod.pk}/")
        assert response.status_code == 200
        assert response.json()["name"] == "hr"

    def test_retrieve_other_company_record_fails(self, api_client):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        self._auth(api_client, company_a)
        mod_b = ModuleRegistry.objects.create(
            company=company_b, name="hr", display_name="HR",
        )
        response = api_client.get(f"/api/v1/core/modules/{mod_b.pk}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestDynamicViewSetOrdering:
    def _auth(self, api_client, company):
        user = UserFactory(company=company)
        token = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

    def test_default_ordering_by_sequence(self, api_client):
        company = CompanyFactory()
        self._auth(api_client, company)
        ModuleRegistry.objects.create(
            company=company, name="z_last", display_name="Z Last", sequence=99,
        )
        ModuleRegistry.objects.create(
            company=company, name="a_first", display_name="A First", sequence=1,
        )
        response = api_client.get("/api/v1/core/modules/")
        results = response.json()
        if isinstance(results, dict):
            results = results["results"]
        assert results[0]["name"] == "a_first"
        assert results[1]["name"] == "z_last"
