import factory
from django.utils import timezone

from core.factories import CompanyFactory
from modules.hr.models import Department, Employee, LeaveRequest, Payroll


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ["company", "name"]
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Department {n}")
    description = ""


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    department = factory.SubFactory(DepartmentFactory, company=factory.SelfAttribute("..company"))
    employee_number = factory.Sequence(lambda n: f"EMP-2026-{n:03d}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}@example.com")
    job_title = "Employee"
    hire_date = factory.LazyFunction(lambda: timezone.now().date())
    status = Employee.Status.ACTIVE
    employee_type = Employee.EmployeeType.FULL_TIME


class LeaveRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LeaveRequest
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    employee = factory.SubFactory(EmployeeFactory, company=factory.SelfAttribute("..company"))
    leave_type = LeaveRequest.LeaveType.ANNUAL
    start_date = factory.LazyFunction(lambda: timezone.now().date())
    end_date = factory.LazyFunction(lambda: timezone.now().date())
    days_requested = 1
    status = LeaveRequest.Status.PENDING
    reason = "Vacation"


class PayrollFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payroll
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    employee = factory.SubFactory(EmployeeFactory, company=factory.SelfAttribute("..company"))
    period_start = factory.LazyFunction(lambda: timezone.now().date().replace(day=1))
    period_end = factory.LazyFunction(lambda: timezone.now().date())
    gross_amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    net_amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    status = Payroll.Status.DRAFT
