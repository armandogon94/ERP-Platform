"""Tests for HR API endpoints."""
import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.hr.factories import DepartmentFactory, EmployeeFactory, LeaveRequestFactory
from modules.hr.models import Employee, LeaveRequest


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


# ─── Departments ─────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestDepartmentAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/hr/departments/")
        assert response.status_code == 401

    def test_list_returns_company_departments(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        DepartmentFactory(company=company, name="Engineering")
        DepartmentFactory(company=company, name="Finance")
        auth(api_client, user)

        response = api_client.get("/api/v1/hr/departments/")
        assert response.status_code == 200
        names = [d["name"] for d in response.json()]
        assert "Engineering" in names
        assert "Finance" in names

    def test_departments_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        DepartmentFactory(company=c1, name="EngineeringA")
        DepartmentFactory(company=c2, name="EngineeringB")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/hr/departments/")
        names = [d["name"] for d in response.json()]
        assert "EngineeringA" in names
        assert "EngineeringB" not in names

    def test_create_department(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/hr/departments/",
            {"name": "Marketing", "description": "Marketing team"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Marketing"


# ─── Employees ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestEmployeeAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/hr/employees/")
        assert response.status_code == 401

    def test_list_returns_company_employees(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        EmployeeFactory(company=company, first_name="Alice", last_name="Smith")
        EmployeeFactory(company=company, first_name="Bob", last_name="Jones")
        auth(api_client, user)

        response = api_client.get("/api/v1/hr/employees/")
        assert response.status_code == 200
        data = response.json()
        first_names = [e["first_name"] for e in data]
        assert "Alice" in first_names
        assert "Bob" in first_names

    def test_employees_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        EmployeeFactory(company=c1, first_name="OnlyC1")
        EmployeeFactory(company=c2, first_name="OnlyC2")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/hr/employees/")
        first_names = [e["first_name"] for e in response.json()]
        assert "OnlyC1" in first_names
        assert "OnlyC2" not in first_names

    def test_create_employee(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        dept = DepartmentFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/hr/employees/",
            {
                "first_name": "Carol",
                "last_name": "White",
                "email": "carol@example.com",
                "job_title": "Engineer",
                "department": dept.pk,
                "status": Employee.Status.ACTIVE,
                "employee_type": Employee.EmployeeType.FULL_TIME,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["first_name"] == "Carol"

    def test_retrieve_employee(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        emp = EmployeeFactory(company=company, first_name="Dave")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/hr/employees/{emp.pk}/")
        assert response.status_code == 200
        assert response.json()["first_name"] == "Dave"

    def test_update_employee_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        emp = EmployeeFactory(company=company, status=Employee.Status.ACTIVE)
        auth(api_client, user)

        response = api_client.patch(
            f"/api/v1/hr/employees/{emp.pk}/",
            {"status": Employee.Status.ON_LEAVE},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == Employee.Status.ON_LEAVE

    def test_cannot_access_other_company_employee(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        emp2 = EmployeeFactory(company=c2)
        user1 = UserFactory(company=c1)
        auth(api_client, user1)

        response = api_client.get(f"/api/v1/hr/employees/{emp2.pk}/")
        assert response.status_code == 404


# ─── Leave Requests ───────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestLeaveRequestAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/hr/leave-requests/")
        assert response.status_code == 401

    def test_list_returns_company_leave_requests(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        emp = EmployeeFactory(company=company)
        LeaveRequestFactory(company=company, employee=emp)
        auth(api_client, user)

        response = api_client.get("/api/v1/hr/leave-requests/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_create_leave_request(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        emp = EmployeeFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/hr/leave-requests/",
            {
                "employee": emp.pk,
                "leave_type": LeaveRequest.LeaveType.ANNUAL,
                "start_date": "2026-05-01",
                "end_date": "2026-05-05",
                "days_requested": 5,
                "reason": "Vacation",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["leave_type"] == LeaveRequest.LeaveType.ANNUAL

    def test_leave_requests_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        LeaveRequestFactory(company=c1, employee=EmployeeFactory(company=c1))
        LeaveRequestFactory(company=c2, employee=EmployeeFactory(company=c2))
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/hr/leave-requests/")
        assert len(response.json()) == 1
