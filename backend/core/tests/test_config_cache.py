"""Tests for the config cache layer and signal-based invalidation."""

import pytest
from django.core.cache import cache

from core.factories import CompanyFactory
from core.models import Industry, IndustryConfigTemplate, ModuleConfig, ModuleRegistry
from core.services.config_service import get_resolved_config


@pytest.fixture(autouse=True)
def clear_cache():
    """Ensure a clean cache state for every test."""
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestConfigCaching:
    def test_first_call_populates_cache(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}},
        )

        # Call once — should hit DB and cache result
        result1 = get_resolved_config(company)

        # Verify cache is populated
        cache_key = f"config:{company.id}:__global__"
        cached = cache.get(cache_key)
        assert cached is not None
        assert cached["terminology"]["Warehouse"] == "Supply Room"

    def test_second_call_uses_cache(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}},
        )

        get_resolved_config(company)

        # Corrupt the DB value — second call should still return cached value
        IndustryConfigTemplate.objects.filter(industry=Industry.DENTAL).update(
            config={"terminology": {"Warehouse": "CHANGED"}}
        )

        result2 = get_resolved_config(company)
        assert result2["terminology"]["Warehouse"] == "Supply Room"

    def test_module_level_cache_key(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"modules": {"inventory": {"display_name": "Supplies"}}},
        )

        get_resolved_config(company, module_name="inventory")

        cache_key = f"config:{company.id}:inventory"
        cached = cache.get(cache_key)
        assert cached is not None


@pytest.mark.django_db
class TestSignalInvalidation:
    def test_saving_industry_template_invalidates_company_cache(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        template = IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}},
        )

        # Populate cache
        get_resolved_config(company)
        cache_key = f"config:{company.id}:__global__"
        assert cache.get(cache_key) is not None

        # Update the template — signal should invalidate all dental companies
        template.config = {"terminology": {"Warehouse": "New Value"}}
        template.save()

        assert cache.get(cache_key) is None

    def test_saving_company_config_json_invalidates_cache(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}},
        )

        get_resolved_config(company)
        cache_key = f"config:{company.id}:__global__"
        assert cache.get(cache_key) is not None

        # Update company config — signal should invalidate
        company.config_json = {"terminology": {"Warehouse": "Overridden"}}
        company.save()

        assert cache.get(cache_key) is None

    def test_saving_module_config_invalidates_company_cache(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={},
        )
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )

        get_resolved_config(company)
        get_resolved_config(company, module_name="inventory")

        cache_key_global = f"config:{company.id}:__global__"
        cache_key_module = f"config:{company.id}:inventory"
        assert cache.get(cache_key_global) is not None
        assert cache.get(cache_key_module) is not None

        # Create a ModuleConfig — should invalidate both cache keys for this company
        ModuleConfig.objects.create(
            company=company,
            module=module,
            key="display_name",
            value="Custom Name",
            value_type="string",
        )

        assert cache.get(cache_key_global) is None
        assert cache.get(cache_key_module) is None

    def test_deleting_module_config_invalidates_cache(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(industry=Industry.DENTAL, config={})
        module = ModuleRegistry.objects.create(
            company=company, name="inventory", display_name="Inventory"
        )
        mc = ModuleConfig.objects.create(
            company=company,
            module=module,
            key="display_name",
            value="Custom",
            value_type="string",
        )

        get_resolved_config(company)
        cache_key = f"config:{company.id}:__global__"
        assert cache.get(cache_key) is not None

        mc.delete()
        assert cache.get(cache_key) is None

    def test_cache_miss_falls_back_to_db(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Product": "Dental Supply"}},
        )

        # No cache yet
        result = get_resolved_config(company)
        assert result["terminology"]["Product"] == "Dental Supply"
