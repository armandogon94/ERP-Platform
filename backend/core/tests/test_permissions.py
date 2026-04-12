import pytest
from django.urls import path
from rest_framework.response import Response
from rest_framework.test import URLPatternsTestCase
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.permissions import IsCompanyAdmin, IsCompanyMember, ModulePermission
from core.factories import (
    CompanyFactory,
    PermissionFactory,
    RoleFactory,
    UserFactory,
)
from core.models import RoleLevel, RolePermission, UserRole


# Test views that use the permission classes
class CompanyMemberView(APIView):
    permission_classes = [IsCompanyMember]

    def get(self, request):
        return Response({"company": request.company.name})


class CompanyAdminView(APIView):
    permission_classes = [IsCompanyMember, IsCompanyAdmin]

    def get(self, request):
        return Response({"admin": True})


class AccountingView(APIView):
    permission_classes = [IsCompanyMember, ModulePermission]
    module_name = "accounting"

    def get(self, request):
        return Response({"module": "accounting"})

    def post(self, request):
        return Response({"created": True})


@pytest.mark.django_db
class TestIsCompanyMember:
    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 401

    def test_authenticated_member_returns_200(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        token = RefreshToken.for_user(user)
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token.access_token}"
        )
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestModulePermission:
    """Tests that ModulePermission correctly gates access based on role permissions."""

    def _setup_user_with_permissions(self, company, codenames):
        user = UserFactory(company=company)
        role = RoleFactory(
            company=company,
            name=f"TestRole-{user.pk}",
            role_level=RoleLevel.OPERATIONAL,
        )
        for codename in codenames:
            perm = PermissionFactory(codename=codename)
            RolePermission.objects.create(role=role, permission=perm)
        UserRole.objects.create(user=user, role=role)
        return user

    def test_user_with_read_permission_can_get(self, api_client):
        """User with accounting.read can GET accounting endpoint."""
        company = CompanyFactory()
        user = self._setup_user_with_permissions(
            company, ["accounting.read"]
        )
        token = RefreshToken.for_user(user)
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token.access_token}"
        )

        # We need to test via a real endpoint — use a URL that exercises ModulePermission.
        # Since we don't have accounting endpoints yet, we verify the permission class directly.
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/fake/")
        request.user = user
        request.permissions = {"accounting.read"}

        view = AccountingView()
        view.module_name = "accounting"

        perm = ModulePermission()
        assert perm.has_permission(request, view) is True

    def test_user_without_permission_denied(self, api_client):
        from django.test import RequestFactory

        company = CompanyFactory()
        user = UserFactory(company=company)

        factory = RequestFactory()
        request = factory.get("/fake/")
        request.user = user
        request.permissions = set()

        view = AccountingView()

        perm = ModulePermission()
        assert perm.has_permission(request, view) is False

    def test_write_action_requires_create_permission(self):
        from django.test import RequestFactory

        company = CompanyFactory()
        user = UserFactory(company=company)

        factory = RequestFactory()
        request = factory.post("/fake/")
        request.user = user
        request.permissions = {"accounting.read"}

        view = AccountingView()

        perm = ModulePermission()
        assert perm.has_permission(request, view) is False

        request.permissions = {"accounting.read", "accounting.create"}
        assert perm.has_permission(request, view) is True

    def test_view_without_module_name_allows_access(self):
        from django.test import RequestFactory

        company = CompanyFactory()
        user = UserFactory(company=company)

        factory = RequestFactory()
        request = factory.get("/fake/")
        request.user = user
        request.permissions = set()

        view = APIView()  # no module_name

        perm = ModulePermission()
        assert perm.has_permission(request, view) is True


@pytest.mark.django_db
class TestIsCompanyAdmin:
    def test_admin_user_allowed(self):
        from django.test import RequestFactory

        company = CompanyFactory()
        user = UserFactory(company=company, is_admin=True)

        factory = RequestFactory()
        request = factory.get("/fake/")
        request.user = user
        request.is_company_admin = True

        perm = IsCompanyAdmin()
        assert perm.has_permission(request, view=None) is True

    def test_non_admin_denied(self):
        from django.test import RequestFactory

        company = CompanyFactory()
        user = UserFactory(company=company, is_admin=False)

        factory = RequestFactory()
        request = factory.get("/fake/")
        request.user = user
        request.is_company_admin = False

        perm = IsCompanyAdmin()
        assert perm.has_permission(request, view=None) is False


@pytest.mark.django_db
class TestCompanyIsolationViaFilter:
    def test_filter_backend_scopes_to_company(self):
        from api.v1.filters import CompanyScopedFilterBackend

        company_a = CompanyFactory()
        company_b = CompanyFactory()

        RoleFactory(company=company_a, name="Role A")
        RoleFactory(company=company_b, name="Role B")

        from django.test import RequestFactory
        from core.models import Role

        factory = RequestFactory()
        request = factory.get("/fake/")
        request.user = UserFactory(company=company_a)
        request.company = company_a

        backend = CompanyScopedFilterBackend()
        qs = backend.filter_queryset(request, Role.objects.all(), view=None)

        assert qs.count() == 1
        assert qs.first().name == "Role A"
