"""Tests for the Industry Config System — 3-tier hierarchy and config service."""

import pytest

from core.factories import CompanyFactory
from core.models import Industry, IndustryConfigTemplate, ModuleConfig, ModuleRegistry
from core.services.config_service import (
    get_company_config,
    get_industry_config,
    get_resolved_config,
    get_terminology,
    merge_configs,
)


# ──────────────────────────────────────────────────────────────────────────────
# merge_configs — deep merge with list-replace semantics
# ──────────────────────────────────────────────────────────────────────────────


class TestMergeConfigs:
    def test_override_wins_on_flat_key(self):
        base = {"color": "blue", "label": "Product"}
        override = {"label": "Supply"}
        result = merge_configs(base, override)
        assert result["label"] == "Supply"
        assert result["color"] == "blue"

    def test_base_keys_preserved_when_not_overridden(self):
        base = {"a": 1, "b": 2}
        override = {"b": 99}
        result = merge_configs(base, override)
        assert result["a"] == 1
        assert result["b"] == 99

    def test_deep_merge_nested_dicts(self):
        base = {"terminology": {"Warehouse": "Warehouse", "Product": "Product"}}
        override = {"terminology": {"Product": "Supply Item"}}
        result = merge_configs(base, override)
        assert result["terminology"]["Warehouse"] == "Warehouse"
        assert result["terminology"]["Product"] == "Supply Item"

    def test_three_level_nesting(self):
        base = {"modules": {"inventory": {"labels": {"main": "Inventory", "sub": "Items"}}}}
        override = {"modules": {"inventory": {"labels": {"sub": "Supplies"}}}}
        result = merge_configs(base, override)
        assert result["modules"]["inventory"]["labels"]["main"] == "Inventory"
        assert result["modules"]["inventory"]["labels"]["sub"] == "Supplies"

    def test_lists_are_replaced_not_merged(self):
        base = {"fields": ["name", "date", "status"]}
        override = {"fields": ["name", "cost"]}
        result = merge_configs(base, override)
        assert result["fields"] == ["name", "cost"]

    def test_empty_override_returns_base(self):
        base = {"x": 1}
        result = merge_configs(base, {})
        assert result == {"x": 1}

    def test_empty_base_returns_override(self):
        override = {"x": 2}
        result = merge_configs({}, override)
        assert result == {"x": 2}

    def test_original_dicts_are_not_mutated(self):
        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        merge_configs(base, override)
        assert "c" not in base["a"]


# ──────────────────────────────────────────────────────────────────────────────
# IndustryConfigTemplate model basics
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestIndustryConfigTemplateModel:
    def test_can_create_template(self):
        t = IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}},
        )
        assert t.pk is not None
        assert t.industry == Industry.DENTAL

    def test_industry_is_unique(self):
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL, config={}
        )
        with pytest.raises(Exception):
            IndustryConfigTemplate.objects.create(
                industry=Industry.DENTAL, config={}
            )

    def test_str_representation(self):
        t = IndustryConfigTemplate(industry=Industry.DENTAL)
        assert "Dental" in str(t)


# ──────────────────────────────────────────────────────────────────────────────
# get_industry_config
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetIndustryConfig:
    def test_returns_config_for_existing_industry(self):
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}},
        )
        result = get_industry_config(Industry.DENTAL)
        assert result["terminology"]["Warehouse"] == "Supply Room"

    def test_returns_empty_dict_when_no_template(self):
        result = get_industry_config(Industry.FINTECH)
        assert result == {}


# ──────────────────────────────────────────────────────────────────────────────
# get_company_config — tier 1+2 merge
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetCompanyConfig:
    def test_returns_industry_defaults_with_no_overrides(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Product": "Dental Supply"}},
        )
        result = get_company_config(company)
        assert result["terminology"]["Product"] == "Dental Supply"

    def test_company_overrides_industry_defaults(self):
        company = CompanyFactory(
            industry=Industry.DENTAL,
            config_json={"terminology": {"Product": "Custom Item"}},
        )
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Product": "Dental Supply", "Warehouse": "Supply Room"}},
        )
        result = get_company_config(company)
        assert result["terminology"]["Product"] == "Custom Item"
        assert result["terminology"]["Warehouse"] == "Supply Room"

    def test_returns_empty_dict_when_no_template_and_no_overrides(self):
        company = CompanyFactory(industry=Industry.FINTECH, config_json={})
        result = get_company_config(company)
        assert result == {}


# ──────────────────────────────────────────────────────────────────────────────
# get_resolved_config — full 3-tier merge
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetResolvedConfig:
    def test_returns_industry_config_without_module_overrides(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}},
        )
        result = get_resolved_config(company)
        assert result["terminology"]["Warehouse"] == "Supply Room"

    def test_module_config_overrides_company_config(self, db):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        module = ModuleRegistry.objects.create(
            company=company,
            name="inventory",
            display_name="Inventory",
        )
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"modules": {"inventory": {"display_name": "Supplies"}}},
        )
        ModuleConfig.objects.create(
            company=company,
            module=module,
            key="display_name",
            value="Custom Supplies",
            value_type="string",
        )
        result = get_resolved_config(company, module_name="inventory")
        assert result["modules"]["inventory"]["display_name"] == "Custom Supplies"

    def test_no_module_name_returns_global_config(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room"}, "defaults": {"currency": "USD"}},
        )
        result = get_resolved_config(company)
        assert "terminology" in result
        assert "defaults" in result


# ──────────────────────────────────────────────────────────────────────────────
# get_terminology — shortcut
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetTerminology:
    def test_returns_terminology_for_dental(self):
        company = CompanyFactory(industry=Industry.DENTAL, config_json={})
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room", "Product": "Dental Supply"}},
        )
        terms = get_terminology(company)
        assert terms["Warehouse"] == "Supply Room"
        assert terms["Product"] == "Dental Supply"

    def test_returns_empty_dict_when_no_terminology_key(self):
        company = CompanyFactory(industry=Industry.FINTECH, config_json={})
        terms = get_terminology(company)
        assert terms == {}

    def test_company_override_applies_to_terminology(self):
        company = CompanyFactory(
            industry=Industry.DENTAL,
            config_json={"terminology": {"Warehouse": "Clinic Storage"}},
        )
        IndustryConfigTemplate.objects.create(
            industry=Industry.DENTAL,
            config={"terminology": {"Warehouse": "Supply Room", "Product": "Dental Supply"}},
        )
        terms = get_terminology(company)
        assert terms["Warehouse"] == "Clinic Storage"
        assert terms["Product"] == "Dental Supply"
