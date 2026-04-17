import datetime
from decimal import Decimal

import factory

from core.factories import CompanyFactory
from modules.hr.factories import EmployeeFactory
from modules.projects.models import Milestone, Project, ProjectTimesheet, Task


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Project {n}")
    code = factory.Sequence(lambda n: f"PRJ-{n:04d}")
    customer = None
    start_date = factory.LazyFunction(lambda: datetime.date(2026, 1, 1))
    end_date = None
    status = Project.Status.PLANNED
    budget = Decimal("0.00")


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    project = factory.SubFactory(
        ProjectFactory, company=factory.SelfAttribute("..company")
    )
    name = factory.Sequence(lambda n: f"Task {n}")
    assignee = None
    status = Task.Status.TODO
    priority = Task.Priority.NORMAL
    due_date = None
    parent_task = None


class MilestoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Milestone
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    project = factory.SubFactory(
        ProjectFactory, company=factory.SelfAttribute("..company")
    )
    name = factory.Sequence(lambda n: f"Milestone {n}")
    due_date = factory.LazyFunction(lambda: datetime.date(2026, 6, 30))
    completed = False


class ProjectTimesheetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectTimesheet
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    project = factory.SubFactory(
        ProjectFactory, company=factory.SelfAttribute("..company")
    )
    task = None
    employee = factory.SubFactory(
        EmployeeFactory, company=factory.SelfAttribute("..company")
    )
    date = factory.LazyFunction(lambda: datetime.date(2026, 1, 15))
    hours = Decimal("8.00")
    billable = True
    description = ""
