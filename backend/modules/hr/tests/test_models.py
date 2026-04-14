"""Tests for HR module models: Employee, Department."""
import pytest
from django.utils import timezone

from core.factories import CompanyFactory, UserFactory
from modules.hr.factories import DepartmentFactory, EmployeeFactory
from modules.hr.models import Department, Employee


@pytest.mark.django_db
class TestDepartmentModel:
    def test_create_department(self):
        company = CompanyFactory()
        dept = Department.objects.create(
            company=company,
            name="Engineering",
        )
        assert dept.pk is not None
        assert dept.name == "Engineering"
        assert dept.company == company

    def test_department_str(self):
        company = CompanyFactory(name="NovaPay")
        dept = Department(company=company, name="Engineering")
        assert "Engineering" in str(dept)

    def test_department_unique_per_company(self):
        company = CompanyFactory()
        Department.objects.create(company=company, name="HR")
        with pytest.raises(Exception):
            Department.objects.create(company=company, name="HR")

    def test_same_name_different_companies_allowed(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        Department.objects.create(company=c1, name="HR")
        dept2 = Department.objects.create(company=c2, name="HR")
        assert dept2.pk is not None

    def test_department_factory(self):
        dept = DepartmentFactory()
        assert dept.pk is not None
        assert dept.company is not None


@pytest.mark.django_db
class TestEmployeeModel:
    def test_create_employee(self):
        company = CompanyFactory()
        dept = DepartmentFactory(company=company)
        emp = Employee.objects.create(
            company=company,
            department=dept,
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            job_title="Engineer",
            hire_date=timezone.now().date(),
            status=Employee.Status.ACTIVE,
            employee_type=Employee.EmployeeType.FULL_TIME,
        )
        assert emp.pk is not None
        assert emp.first_name == "Alice"

    def test_employee_str_contains_name(self):
        emp = EmployeeFactory(first_name="Bob", last_name="Jones")
        assert "Bob" in str(emp)
        assert "Jones" in str(emp)

    def test_employee_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        EmployeeFactory(company=c1)
        EmployeeFactory(company=c2)
        assert Employee.objects.filter(company=c1).count() == 1
        assert Employee.objects.filter(company=c2).count() == 1

    def test_employee_status_choices(self):
        emp = EmployeeFactory(status=Employee.Status.ACTIVE)
        assert emp.status == Employee.Status.ACTIVE

    def test_employee_soft_delete(self):
        emp = EmployeeFactory()
        emp.soft_delete()
        assert Employee.objects.filter(pk=emp.pk).count() == 0
        assert Employee.all_objects.filter(pk=emp.pk).count() == 1

    def test_employee_type_choices(self):
        emp = EmployeeFactory(employee_type=Employee.EmployeeType.CONTRACTOR)
        assert emp.employee_type == Employee.EmployeeType.CONTRACTOR

    def test_employee_factory(self):
        emp = EmployeeFactory()
        assert emp.pk is not None
        assert emp.department is not None
        assert emp.company is not None

    def test_employee_number_field_exists(self):
        emp = EmployeeFactory(employee_number="EMP-2026-001")
        assert emp.employee_number == "EMP-2026-001"
