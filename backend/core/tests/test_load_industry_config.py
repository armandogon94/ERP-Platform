"""Tests for the load_industry_config management command."""

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from core.models import Industry, IndustryConfigTemplate


@pytest.mark.django_db
class TestLoadIndustryConfigCommand:
    def test_loads_all_10_industries(self):
        call_command("load_industry_config", verbosity=0)
        count = IndustryConfigTemplate.objects.count()
        assert count == 10

    def test_dental_has_warehouse_terminology(self):
        call_command("load_industry_config", verbosity=0)
        dental = IndustryConfigTemplate.objects.get(industry=Industry.DENTAL)
        terminology = dental.config.get("terminology", {})
        assert terminology.get("Warehouse") == "Supply Room"

    def test_dental_has_product_terminology(self):
        call_command("load_industry_config", verbosity=0)
        dental = IndustryConfigTemplate.objects.get(industry=Industry.DENTAL)
        terminology = dental.config.get("terminology", {})
        assert terminology.get("Product") == "Dental Supply"

    def test_hospitality_has_product_as_menu_item(self):
        call_command("load_industry_config", verbosity=0)
        hosp = IndustryConfigTemplate.objects.get(industry=Industry.HOSPITALITY)
        terminology = hosp.config.get("terminology", {})
        assert terminology.get("Product") == "Menu Item"

    def test_all_industries_have_terminology_key(self):
        call_command("load_industry_config", verbosity=0)
        for template in IndustryConfigTemplate.objects.all():
            assert "terminology" in template.config, (
                f"{template.industry} config is missing 'terminology' key"
            )

    def test_command_is_idempotent(self):
        call_command("load_industry_config", verbosity=0)
        call_command("load_industry_config", verbosity=0)
        count = IndustryConfigTemplate.objects.count()
        assert count == 10

    def test_load_single_industry_flag(self):
        call_command("load_industry_config", "--industry", "dental", verbosity=0)
        assert IndustryConfigTemplate.objects.count() == 1
        assert IndustryConfigTemplate.objects.filter(industry=Industry.DENTAL).exists()

    def test_dry_run_does_not_write_to_db(self):
        call_command("load_industry_config", "--dry-run", verbosity=0)
        assert IndustryConfigTemplate.objects.count() == 0

    def test_invalid_industry_raises_error(self):
        with pytest.raises((CommandError, SystemExit, Exception)):
            call_command("load_industry_config", "--industry", "notanindustry", verbosity=0)

    def test_all_industry_configs_have_modules_key(self):
        call_command("load_industry_config", verbosity=0)
        for template in IndustryConfigTemplate.objects.all():
            assert "modules" in template.config, (
                f"{template.industry} config is missing 'modules' key"
            )
