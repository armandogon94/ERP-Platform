import pytest

from core.factories import (
    CompanyFactory,
    IndustryRoleTemplateFactory,
    PermissionFactory,
    RoleFactory,
    UserFactory,
)
from core.models import (
    Industry,
    IndustryRoleTemplate,
    Permission,
    Role,
    RoleLevel,
    RolePermission,
    UserRole,
)
from core.services.company_provisioning import provision_company_roles


@pytest.mark.django_db
class TestRBACModels:
    def test_create_permission(self):
        perm = PermissionFactory(codename="accounting.read")
        assert perm.module == "accounting"
        assert perm.action == "read"
        assert str(perm) == "accounting.read"

    def test_create_role(self):
        company = CompanyFactory(slug="testco")
        role = RoleFactory(
            company=company,
            name="Accountant",
            role_level=RoleLevel.OPERATIONAL,
        )
        assert str(role) == "Accountant (testco)"
        assert role.is_system is False

    def test_role_permission_assignment(self):
        company = CompanyFactory()
        role = RoleFactory(company=company, name="Accountant")
        perm_read = PermissionFactory(codename="accounting.read")
        perm_write = PermissionFactory(codename="accounting.write")

        RolePermission.objects.create(role=role, permission=perm_read)
        RolePermission.objects.create(role=role, permission=perm_write)

        assert role.permissions.count() == 2
        codenames = set(role.permissions.values_list("codename", flat=True))
        assert codenames == {"accounting.read", "accounting.write"}

    def test_role_permission_unique_together(self):
        company = CompanyFactory()
        role = RoleFactory(company=company)
        perm = PermissionFactory(codename="hr.read")
        RolePermission.objects.create(role=role, permission=perm)

        with pytest.raises(Exception):
            RolePermission.objects.create(role=role, permission=perm)

    def test_user_role_assignment(self):
        company = CompanyFactory()
        user = UserFactory(company=company)
        role = RoleFactory(company=company, name="Manager")

        UserRole.objects.create(user=user, role=role)
        assert user.user_roles.count() == 1
        assert user.user_roles.first().role.name == "Manager"

    def test_role_unique_per_company(self):
        company = CompanyFactory()
        RoleFactory(company=company, name="Admin")
        with pytest.raises(Exception):
            RoleFactory(company=company, name="Admin")

    def test_same_role_name_different_companies(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        role_a = RoleFactory(company=company_a, name="Admin")
        role_b = RoleFactory(company=company_b, name="Admin")
        assert role_a.pk != role_b.pk

    def test_industry_role_template_creation(self):
        template = IndustryRoleTemplateFactory(
            industry=Industry.FINTECH,
            role_slug="financial-analyst",
            role_name="Financial Analyst",
            role_level=RoleLevel.OPERATIONAL,
            module_permissions=["accounting.read", "invoicing.read"],
        )
        assert template.industry == Industry.FINTECH
        assert template.module_permissions == ["accounting.read", "invoicing.read"]

    def test_template_unique_per_industry(self):
        IndustryRoleTemplate.objects.create(
            industry=Industry.FINTECH,
            role_slug="analyst",
            role_name="Analyst",
            role_level=RoleLevel.OPERATIONAL,
        )
        with pytest.raises(Exception):
            IndustryRoleTemplate.objects.create(
                industry=Industry.FINTECH,
                role_slug="analyst",
                role_name="Analyst Dupe",
                role_level=RoleLevel.OPERATIONAL,
            )

    def test_same_slug_different_industries(self):
        t1 = IndustryRoleTemplateFactory(
            industry=Industry.FINTECH,
            role_slug="manager",
        )
        t2 = IndustryRoleTemplateFactory(
            industry=Industry.HEALTHCARE,
            role_slug="manager",
        )
        assert t1.pk != t2.pk


@pytest.mark.django_db
class TestCompanyProvisioning:
    def test_provision_creates_roles_from_templates(self):
        PermissionFactory(codename="accounting.read")
        PermissionFactory(codename="accounting.write")

        IndustryRoleTemplateFactory(
            industry=Industry.FINTECH,
            role_slug="analyst",
            role_name="Financial Analyst",
            role_level=RoleLevel.OPERATIONAL,
            module_permissions=["accounting.read"],
        )
        IndustryRoleTemplateFactory(
            industry=Industry.FINTECH,
            role_slug="cfo",
            role_name="Chief Financial Officer",
            role_level=RoleLevel.EXECUTIVE,
            module_permissions=["accounting.read", "accounting.write"],
        )

        company = CompanyFactory(industry=Industry.FINTECH)
        roles = provision_company_roles(company)

        assert len(roles) == 2
        assert Role.objects.filter(company=company).count() == 2

        cfo = Role.objects.get(company=company, name="Chief Financial Officer")
        assert cfo.is_system is True
        assert cfo.role_level == RoleLevel.EXECUTIVE
        assert cfo.permissions.count() == 2

    def test_provision_skips_other_industries(self):
        IndustryRoleTemplateFactory(
            industry=Industry.HEALTHCARE,
            role_slug="doctor",
            role_name="Doctor",
        )

        company = CompanyFactory(industry=Industry.FINTECH)
        roles = provision_company_roles(company)

        assert len(roles) == 0
        assert Role.objects.filter(company=company).count() == 0

    def test_provision_is_idempotent(self):
        IndustryRoleTemplateFactory(
            industry=Industry.FINTECH,
            role_slug="analyst",
            role_name="Analyst",
        )

        company = CompanyFactory(industry=Industry.FINTECH)
        provision_company_roles(company)
        provision_company_roles(company)

        assert Role.objects.filter(company=company).count() == 1

    def test_provision_skips_unknown_permissions(self):
        IndustryRoleTemplateFactory(
            industry=Industry.FINTECH,
            role_slug="analyst",
            role_name="Analyst",
            module_permissions=["nonexistent.read"],
        )

        company = CompanyFactory(industry=Industry.FINTECH)
        roles = provision_company_roles(company)

        assert len(roles) == 1
        assert roles[0].permissions.count() == 0

    def test_role_soft_delete(self):
        company = CompanyFactory()
        role = RoleFactory(company=company, name="Temp Role")
        role.soft_delete()

        assert Role.objects.filter(company=company).count() == 0
        assert Role.all_objects.filter(company=company).count() == 1

        role.restore()
        assert Role.objects.filter(company=company).count() == 1
