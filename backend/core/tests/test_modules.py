import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from core.models import ModuleConfig, ModuleRegistry


@pytest.mark.django_db
class TestModuleRegistry:
    def test_create_module(self):
        company = CompanyFactory()
        mod = ModuleRegistry(
            company=company,
            name="accounting",
            display_name="Accounting",
            icon="calculator",
            sequence=1,
        )
        mod.save()
        assert mod.pk is not None
        assert str(mod) == f"Accounting ({company.slug})"

    def test_module_unique_per_company(self):
        company = CompanyFactory()
        ModuleRegistry.objects.create(
            company=company, name="hr", display_name="HR",
        )
        with pytest.raises(Exception):
            ModuleRegistry.objects.create(
                company=company, name="hr", display_name="HR Dupe",
            )

    def test_module_config_storage(self):
        company = CompanyFactory()
        mod = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory",
        )
        cfg = ModuleConfig.objects.create(
            company=company,
            module=mod,
            key="warehouse_label",
            value="Supply Room",
            value_type="string",
        )
        assert str(cfg) == "inventory.warehouse_label"


@pytest.mark.django_db
class TestModuleAPI:
    def test_list_modules_requires_auth(self, api_client):
        response = api_client.get("/api/v1/core/modules/")
        assert response.status_code == 401

    def test_list_modules_returns_company_modules(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        ModuleRegistry.objects.create(
            company=company, name="accounting", display_name="Accounting", sequence=1,
        )
        ModuleRegistry.objects.create(
            company=company, name="hr", display_name="HR", sequence=2,
        )

        token = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

        response = api_client.get("/api/v1/core/modules/")
        assert response.status_code == 200
        results = response.json()
        if isinstance(results, dict):
            results = results["results"]
        assert len(results) == 2
        assert results[0]["name"] == "accounting"

    def test_modules_scoped_to_company(self, api_client):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        ModuleRegistry.objects.create(
            company=company_a, name="accounting", display_name="Accounting",
        )
        ModuleRegistry.objects.create(
            company=company_b, name="hr", display_name="HR",
        )

        user_a = UserFactory(company=company_a)
        token = RefreshToken.for_user(user_a)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

        response = api_client.get("/api/v1/core/modules/")
        results = response.json()
        if isinstance(results, dict):
            results = results["results"]
        assert len(results) == 1
        assert results[0]["name"] == "accounting"
