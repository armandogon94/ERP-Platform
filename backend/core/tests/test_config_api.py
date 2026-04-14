"""Tests for the enhanced module config API (GET resolved + PATCH overrides)."""

import pytest
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from core.models import Industry, IndustryConfigTemplate, ModuleRegistry


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


def make_auth_client(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestModuleConfigGET:
    def test_get_config_requires_auth(self, api_client):
        company = CompanyFactory()
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )
        response = api_client.get(f"/api/v1/core/modules/{module.pk}/config/")
        assert response.status_code == 401

    def test_get_config_returns_resolved_config(self, api_client):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        user = UserFactory(company=company)
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={
                "terminology": {"Warehouse": "Supply Room", "Product": "Dental Supply"},
                "modules": {"inventory": {"display_name": "Supplies"}},
            },
        )
        make_auth_client(api_client, user)

        response = api_client.get(f"/api/v1/core/modules/{module.pk}/config/")
        assert response.status_code == 200
        data = response.json()

        assert data["module"] == "inventory"
        assert data["industry"] == Industry.DENTAL
        assert data["terminology"]["Warehouse"] == "Supply Room"
        assert data["terminology"]["Product"] == "Dental Supply"

    def test_get_config_includes_module_specific_config(self, api_client):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        user = UserFactory(company=company)
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"modules": {"inventory": {"display_name": "Supplies"}}},
        )
        make_auth_client(api_client, user)

        response = api_client.get(f"/api/v1/core/modules/{module.pk}/config/")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["modules"]["inventory"]["display_name"] == "Supplies"

    def test_get_config_returns_empty_when_no_template(self, api_client):
        company = CompanyFactory(industry=Industry.FINTECH, config_json={})
        user = UserFactory(company=company)
        module = ModuleRegistry.objects.create(
            company=company, name="accounting", display_name="Accounting"
        )
        make_auth_client(api_client, user)

        response = api_client.get(f"/api/v1/core/modules/{module.pk}/config/")
        assert response.status_code == 200
        data = response.json()
        assert data["terminology"] == {}
        assert data["config"] == {}


@pytest.mark.django_db
class TestModuleConfigPATCH:
    def test_patch_requires_company_admin(self, api_client):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        user = UserFactory(company=company, is_admin=False)
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )
        make_auth_client(api_client, user)

        response = api_client.patch(
            f"/api/v1/core/modules/{module.pk}/config/",
            {"overrides": {"terminology": {"Warehouse": "My Storage"}}},
            format="json",
        )
        assert response.status_code == 403

    def test_patch_saves_company_override(self, api_client):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        user = UserFactory(company=company, is_admin=True)
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}},
        )
        make_auth_client(api_client, user)

        response = api_client.patch(
            f"/api/v1/core/modules/{module.pk}/config/",
            {"overrides": {"terminology": {"Warehouse": "Clinic Storage"}}},
            format="json",
        )
        assert response.status_code == 200

        # Reload company from DB and verify override was saved
        company.refresh_from_db()
        assert company.config_json["terminology"]["Warehouse"] == "Clinic Storage"

    def test_patch_returns_updated_resolved_config(self, api_client):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        user = UserFactory(company=company, is_admin=True)
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room", "Product": "Dental Supply"}},
        )
        make_auth_client(api_client, user)

        response = api_client.patch(
            f"/api/v1/core/modules/{module.pk}/config/",
            {"overrides": {"terminology": {"Warehouse": "Clinic Storage"}}},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()

        # Override applied
        assert data["terminology"]["Warehouse"] == "Clinic Storage"
        # Industry default preserved for non-overridden key
        assert data["terminology"]["Product"] == "Dental Supply"

    def test_patch_invalidates_cache(self, api_client):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        user = UserFactory(company=company, is_admin=True)
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}},
        )
        make_auth_client(api_client, user)

        # Pre-populate cache via GET (module-scoped key)
        api_client.get(f"/api/v1/core/modules/{module.pk}/config/")

        from django.core.cache import cache as django_cache
        cache_key = f"config:{company.id}:inventory"
        assert django_cache.get(cache_key) is not None

        # PATCH should invalidate old cache and repopulate with new value
        api_client.patch(
            f"/api/v1/core/modules/{module.pk}/config/",
            {"overrides": {"terminology": {"Warehouse": "New Value"}}},
            format="json",
        )
        # Cache is repopulated by the PATCH response with the updated config
        updated_cached = django_cache.get(cache_key)
        assert updated_cached is not None
        assert updated_cached["terminology"]["Warehouse"] == "New Value"

    def test_patch_requires_auth(self, api_client):
        company = CompanyFactory()
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )
        response = api_client.patch(
            f"/api/v1/core/modules/{module.pk}/config/",
            {"overrides": {}},
            format="json",
        )
        assert response.status_code == 401
