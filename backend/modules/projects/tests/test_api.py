"""API tests for the Projects module."""

from decimal import Decimal

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, PartnerFactory, UserFactory
from modules.hr.factories import EmployeeFactory
from modules.projects.factories import (
    MilestoneFactory,
    ProjectFactory,
    ProjectTimesheetFactory,
    TaskFactory,
)


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestProjectAPI:
    def test_list_requires_auth(self, api_client):
        assert api_client.get("/api/v1/projects/projects/").status_code == 401

    def test_list_scopes_to_company(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        ProjectFactory(company=company, name="Ours")
        ProjectFactory(name="Theirs")
        auth(api_client, user)

        response = api_client.get("/api/v1/projects/projects/")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert "Ours" in names
        assert "Theirs" not in names

    def test_create_project_with_partner_customer(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        partner = PartnerFactory(company=company, is_customer=True, name="Big Client")
        auth(api_client, user)

        payload = {
            "name": "New Tower",
            "code": "NT-1",
            "customer": partner.id,
            "status": "active",
            "budget": "50000.00",
        }
        response = api_client.post(
            "/api/v1/projects/projects/", payload, format="json"
        )
        assert response.status_code == 201, response.content
        assert response.json()["customer"] == partner.id

    def test_filter_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        ProjectFactory(company=company, name="Act-1", status="active")
        ProjectFactory(company=company, name="Plan-1", status="planned")
        auth(api_client, user)

        response = api_client.get("/api/v1/projects/projects/?status=active")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert names == ["Act-1"]

    def test_progress_action_returns_aggregate(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        employee = EmployeeFactory(company=company)
        project = ProjectFactory(
            company=company,
            name="Prog",
            budget=Decimal("10000.00"),
        )
        TaskFactory(company=company, project=project, status="done")
        TaskFactory(company=company, project=project, status="todo")
        TaskFactory(company=company, project=project, status="in_progress")
        ProjectTimesheetFactory(
            company=company, project=project, employee=employee,
            hours=Decimal("5.00"),
        )
        ProjectTimesheetFactory(
            company=company, project=project, employee=employee,
            hours=Decimal("2.50"),
        )
        auth(api_client, user)

        response = api_client.get(
            f"/api/v1/projects/projects/{project.pk}/progress/"
        )
        assert response.status_code == 200, response.content
        body = response.json()
        assert body["total_tasks"] == 3
        assert body["done"] == 1
        # 7.50 hours logged as a float/string — accept either shape
        assert float(body["hours_logged"]) == 7.5
        assert "budget_consumed_pct" in body

    def test_cross_company_404(self, api_client):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        user_a = UserFactory(company=a)
        p_b = ProjectFactory(company=b)
        auth(api_client, user_a)
        assert api_client.get(
            f"/api/v1/projects/projects/{p_b.pk}/"
        ).status_code == 404


@pytest.mark.django_db
class TestTaskAPI:
    def test_list_filters_by_project(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        p1 = ProjectFactory(company=company, name="P1")
        p2 = ProjectFactory(company=company, name="P2")
        TaskFactory(company=company, project=p1, name="T1")
        TaskFactory(company=company, project=p2, name="T2")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/projects/tasks/?project={p1.id}")
        assert response.status_code == 200
        names = [t["name"] for t in response.json()]
        assert names == ["T1"]

    def test_list_filters_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        TaskFactory(company=company, name="A", status="done")
        TaskFactory(company=company, name="B", status="todo")
        auth(api_client, user)

        response = api_client.get("/api/v1/projects/tasks/?status=done")
        names = [t["name"] for t in response.json()]
        assert names == ["A"]


@pytest.mark.django_db
class TestMilestoneAPI:
    def test_create(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        project = ProjectFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/projects/milestones/",
            {"project": project.id, "name": "Phase 1"},
            format="json",
        )
        assert response.status_code == 201, response.content


@pytest.mark.django_db
class TestTimesheetAPI:
    def test_filter_by_project(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        emp = EmployeeFactory(company=company)
        p1 = ProjectFactory(company=company)
        p2 = ProjectFactory(company=company)
        ProjectTimesheetFactory(company=company, project=p1, employee=emp)
        ProjectTimesheetFactory(company=company, project=p2, employee=emp)
        auth(api_client, user)

        response = api_client.get(
            f"/api/v1/projects/timesheets/?project={p1.id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
