"""Model tests for the Projects module (Slice 12)."""

import datetime
from decimal import Decimal

import pytest

from core.factories import CompanyFactory, PartnerFactory
from modules.hr.factories import EmployeeFactory
from modules.projects.factories import (
    MilestoneFactory,
    ProjectFactory,
    ProjectTimesheetFactory,
    TaskFactory,
)
from modules.projects.models import Milestone, Project, ProjectTimesheet, Task


@pytest.mark.django_db
class TestProject:
    def test_create_project(self):
        p = ProjectFactory()
        assert p.pk is not None
        assert p.status == Project.Status.PLANNED

    def test_str_returns_name(self):
        p = ProjectFactory(name="North Tower Build")
        assert str(p) == "North Tower Build"

    def test_customer_nullable(self):
        p = ProjectFactory(customer=None)
        assert p.customer is None

    def test_assign_customer_partner(self):
        company = CompanyFactory()
        partner = PartnerFactory(company=company, is_customer=True)
        p = ProjectFactory(company=company, customer=partner)
        assert p.customer_id == partner.id

    def test_company_isolation(self):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        ProjectFactory(company=a, code="A-1")
        ProjectFactory(company=b, code="B-1")
        assert Project.objects.filter(company=a).count() == 1
        assert Project.objects.filter(company=b).count() == 1

    def test_budget_decimal(self):
        p = ProjectFactory(budget=Decimal("150000.00"))
        assert p.budget == Decimal("150000.00")


@pytest.mark.django_db
class TestTask:
    def test_create_task(self):
        t = TaskFactory()
        assert t.pk is not None
        assert t.status == Task.Status.TODO

    def test_assignee_optional(self):
        t = TaskFactory(assignee=None)
        assert t.assignee is None

    def test_assign_same_company_employee(self):
        company = CompanyFactory()
        employee = EmployeeFactory(company=company)
        t = TaskFactory(company=company, assignee=employee)
        assert t.assignee_id == employee.id

    def test_parent_task_self_fk(self):
        company = CompanyFactory()
        parent = TaskFactory(company=company, name="Parent")
        child = TaskFactory(company=company, parent_task=parent, name="Subtask")
        assert child.parent_task_id == parent.id

    def test_status_choices(self):
        t = TaskFactory(status=Task.Status.DONE)
        assert t.status == "done"


@pytest.mark.django_db
class TestMilestone:
    def test_create_milestone(self):
        m = MilestoneFactory()
        assert m.pk is not None
        assert m.completed is False

    def test_due_date_optional(self):
        m = MilestoneFactory(due_date=None)
        assert m.due_date is None


@pytest.mark.django_db
class TestProjectTimesheet:
    def test_create_timesheet(self):
        ts = ProjectTimesheetFactory()
        assert ts.pk is not None
        assert ts.hours > 0

    def test_billable_flag(self):
        ts = ProjectTimesheetFactory(billable=True)
        assert ts.billable is True

    def test_task_nullable(self):
        ts = ProjectTimesheetFactory(task=None)
        assert ts.task is None

    def test_hours_decimal_precision(self):
        ts = ProjectTimesheetFactory(hours=Decimal("7.50"))
        assert ts.hours == Decimal("7.50")
