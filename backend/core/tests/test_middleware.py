import pytest
from django.test import RequestFactory
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import (
    CompanyFactory,
    PermissionFactory,
    RoleFactory,
    UserFactory,
)
from core.models import RoleLevel, RolePermission, UserRole


@pytest.mark.django_db
class TestCompanyRoleContextMiddleware:
    def test_unauthenticated_request_has_none_company(self, api_client):
        """Middleware doesn't crash on unauthenticated requests."""
        response = api_client.get("/api/v1/")
        assert response.status_code == 200

    def test_authenticated_user_gets_company_context(self, api_client):
        company = CompanyFactory(name="TestCo", slug="testco")
        user = UserFactory(company=company)
        token = RefreshToken.for_user(user)
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token.access_token}"
        )

        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 200
        assert response.json()["company"]["name"] == "TestCo"

    def test_middleware_populates_permissions(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        role = RoleFactory(
            company=company,
            name="Accountant",
            role_level=RoleLevel.OPERATIONAL,
        )
        perm = PermissionFactory(codename="accounting.read")
        RolePermission.objects.create(role=role, permission=perm)
        UserRole.objects.create(user=user, role=role)

        token = RefreshToken.for_user(user)
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token.access_token}"
        )

        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 200
