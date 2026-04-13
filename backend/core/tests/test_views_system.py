import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from core.models import ViewDefinition


@pytest.mark.django_db
class TestViewDefinitionModel:
    def test_create_list_view(self):
        company = CompanyFactory()
        view = ViewDefinition.objects.create(
            company=company,
            model_name="hr.employee",
            view_type="list",
            name="Employee List",
            is_default=True,
            config={
                "columns": [
                    {"field": "name", "label": "Name", "sortable": True},
                    {"field": "department", "label": "Department", "sortable": True},
                    {"field": "job_title", "label": "Job Title"},
                ],
                "default_order": "-name",
                "search_fields": ["name", "department"],
            },
        )
        assert view.pk is not None
        assert view.view_type == "list"
        assert len(view.config["columns"]) == 3
        assert str(view) == "Employee List (list)"

    def test_create_form_view(self):
        company = CompanyFactory()
        view = ViewDefinition.objects.create(
            company=company,
            model_name="hr.employee",
            view_type="form",
            name="Employee Form",
            config={
                "sections": [
                    {
                        "title": "Personal Info",
                        "fields": [
                            {"field": "name", "type": "char", "required": True},
                            {"field": "email", "type": "char"},
                            {"field": "department", "type": "many2one", "relation": "hr.department"},
                        ],
                    },
                ],
            },
        )
        assert view.view_type == "form"
        assert len(view.config["sections"]) == 1

    def test_create_kanban_view(self):
        company = CompanyFactory()
        view = ViewDefinition.objects.create(
            company=company,
            model_name="helpdesk.ticket",
            view_type="kanban",
            name="Ticket Kanban",
            config={
                "column_field": "stage",
                "columns": [
                    {"value": "new", "label": "New", "color": "#3B82F6"},
                    {"value": "in_progress", "label": "In Progress", "color": "#F59E0B"},
                    {"value": "done", "label": "Done", "color": "#10B981"},
                ],
                "card_fields": ["name", "priority", "assigned_to"],
            },
        )
        assert view.view_type == "kanban"
        assert view.config["column_field"] == "stage"

    def test_default_view_unique_per_model_type_company(self):
        company = CompanyFactory()
        ViewDefinition.objects.create(
            company=company,
            model_name="hr.employee",
            view_type="list",
            name="Default List",
            is_default=True,
            config={"columns": []},
        )
        with pytest.raises(Exception):
            ViewDefinition.objects.create(
                company=company,
                model_name="hr.employee",
                view_type="list",
                name="Another List",
                is_default=True,
                config={"columns": []},
            )

    def test_non_default_views_allowed(self):
        company = CompanyFactory()
        ViewDefinition.objects.create(
            company=company,
            model_name="hr.employee",
            view_type="list",
            name="Default List",
            is_default=True,
            config={"columns": []},
        )
        view2 = ViewDefinition.objects.create(
            company=company,
            model_name="hr.employee",
            view_type="list",
            name="Compact List",
            is_default=False,
            config={"columns": []},
        )
        assert view2.pk is not None

    def test_view_scoped_to_company(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        ViewDefinition.objects.create(
            company=company_a,
            model_name="hr.employee",
            view_type="list",
            name="A List",
            is_default=True,
            config={"columns": []},
        )
        view_b = ViewDefinition.objects.create(
            company=company_b,
            model_name="hr.employee",
            view_type="list",
            name="B List",
            is_default=True,
            config={"columns": []},
        )
        assert view_b.pk is not None  # same model+type but different company is OK

    def test_view_type_choices(self):
        company = CompanyFactory()
        for vtype in ["list", "form", "kanban", "pivot", "graph"]:
            view = ViewDefinition.objects.create(
                company=company,
                model_name=f"test.{vtype}",
                view_type=vtype,
                name=f"Test {vtype}",
                config={},
            )
            assert view.view_type == vtype


@pytest.mark.django_db
class TestViewDefinitionAPI:
    def test_list_views_requires_auth(self, api_client):
        response = api_client.get("/api/v1/core/views/")
        assert response.status_code == 401

    def test_list_views_for_model(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        ViewDefinition.objects.create(
            company=company,
            model_name="hr.employee",
            view_type="list",
            name="Employee List",
            config={"columns": []},
        )
        ViewDefinition.objects.create(
            company=company,
            model_name="hr.employee",
            view_type="form",
            name="Employee Form",
            config={"sections": []},
        )
        ViewDefinition.objects.create(
            company=company,
            model_name="sales.order",
            view_type="list",
            name="SO List",
            config={"columns": []},
        )

        token = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

        response = api_client.get("/api/v1/core/views/?model_name=hr.employee")
        assert response.status_code == 200
        results = response.json()
        if isinstance(results, dict):
            results = results["results"]
        assert len(results) == 2

    def test_views_scoped_to_company(self, api_client):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        ViewDefinition.objects.create(
            company=company_a, model_name="hr.employee", view_type="list",
            name="A", config={},
        )
        ViewDefinition.objects.create(
            company=company_b, model_name="hr.employee", view_type="list",
            name="B", config={},
        )

        user_a = UserFactory(company=company_a)
        token = RefreshToken.for_user(user_a)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

        response = api_client.get("/api/v1/core/views/")
        results = response.json()
        if isinstance(results, dict):
            results = results["results"]
        assert len(results) == 1
        assert results[0]["name"] == "A"

    def test_get_default_view(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        ViewDefinition.objects.create(
            company=company, model_name="hr.employee", view_type="list",
            name="Default", is_default=True, config={"columns": [{"field": "name"}]},
        )
        ViewDefinition.objects.create(
            company=company, model_name="hr.employee", view_type="list",
            name="Custom", is_default=False, config={"columns": []},
        )

        token = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

        response = api_client.get(
            "/api/v1/core/views/default/?model_name=hr.employee&view_type=list"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Default"
        assert data["is_default"] is True
