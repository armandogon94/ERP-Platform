"""Tests for demo-seed management commands (Slice 17)."""

from io import StringIO

import pytest
from django.core.management import call_command

from core.factories import CompanyFactory, UserFactory
from core.industry_modules import modules_for_industry
from modules.accounting.models import Account
from modules.fleet.models import Vehicle
from modules.helpdesk.models import Ticket, TicketCategory
from modules.hr.models import Employee
from modules.inventory.models import Product
from modules.invoicing.models import Invoice
from modules.manufacturing.models import BillOfMaterials
from modules.pos.models import POSSession
from modules.projects.models import Project
from modules.purchasing.models import Vendor
from modules.reports.models import ReportTemplate
from modules.sales.models import SalesOrder


SEED_COMMANDS = [
    ("seed_hr_demo", Employee),
    ("seed_inventory_demo", Product),
    ("seed_sales_demo", SalesOrder),
    ("seed_purchasing_demo", Vendor),
    ("seed_invoicing_demo", Invoice),
    ("seed_accounting_demo", Account),
    ("seed_fleet_demo", Vehicle),
    ("seed_projects_demo", Project),
    ("seed_manufacturing_demo", BillOfMaterials),
    ("seed_pos_demo", POSSession),
    ("seed_helpdesk_demo", TicketCategory),
    ("seed_reports_demo", ReportTemplate),
]


@pytest.mark.django_db
@pytest.mark.parametrize("cmd,model", SEED_COMMANDS)
def test_seed_command_creates_rows(cmd, model):
    company = CompanyFactory()
    # POS seeder needs a user associated with the company to stamp opened_by.
    UserFactory(company=company)
    out = StringIO()
    call_command(cmd, company=company.slug, stdout=out)
    assert model.objects.filter(company=company).count() > 0


@pytest.mark.django_db
@pytest.mark.parametrize("cmd,model", SEED_COMMANDS)
def test_seed_command_is_idempotent(cmd, model):
    company = CompanyFactory()
    UserFactory(company=company)
    out = StringIO()
    call_command(cmd, company=company.slug, stdout=out)
    first = model.objects.filter(company=company).count()
    call_command(cmd, company=company.slug, stdout=out)
    second = model.objects.filter(company=company).count()
    assert first == second


@pytest.mark.django_db
def test_seed_calendar_demo_creates_events():
    from modules.calendar.models import Event

    company = CompanyFactory()
    call_command("seed_calendar_demo", company=company.slug, stdout=StringIO())
    assert Event.objects.filter(company=company).count() > 0


@pytest.mark.django_db
def test_seed_command_errors_on_unknown_company():
    from django.core.management.base import CommandError

    with pytest.raises(CommandError):
        call_command("seed_hr_demo", company="nonexistent-slug", stdout=StringIO())


@pytest.mark.django_db
def test_industry_modules_includes_base():
    # Base modules (hr, calendar) are always present.
    for industry in ["fintech", "hospitality", "construction"]:
        modules = modules_for_industry(industry)
        assert "hr" in modules
        assert "calendar" in modules


@pytest.mark.django_db
def test_seed_industry_demo_dispatches_per_industry():
    """Meta-command must seed modules appropriate for the industry."""
    company = CompanyFactory(slug="test-hospitality", industry="hospitality")
    UserFactory(company=company)
    call_command(
        "seed_industry_demo", company=company.slug, stdout=StringIO()
    )
    # Hospitality gets inventory, manufacturing, pos, helpdesk.
    assert Product.objects.filter(company=company).count() > 0
    assert BillOfMaterials.objects.filter(company=company).count() > 0
    assert POSSession.objects.filter(company=company).count() > 0
    assert TicketCategory.objects.filter(company=company).count() > 0


@pytest.mark.django_db
def test_seed_industry_demo_fintech_gets_accounting():
    company = CompanyFactory(slug="test-fintech", industry="fintech")
    call_command(
        "seed_industry_demo", company=company.slug, stdout=StringIO()
    )
    # FinTech gets accounting + invoicing + sales + reports.
    assert Account.objects.filter(company=company).count() > 0
    assert Invoice.objects.filter(company=company).count() > 0
