import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

from core.models import Company, IndustryRoleTemplate, Permission, Role, UserProfile


@pytest.mark.django_db
class TestSeedCoreCommand:
    def test_creates_10_companies(self):
        call_command("seed_core")
        assert Company.objects.count() == 10

    def test_creates_52_permissions(self):
        """13 modules x 4 actions = 52 permissions."""
        call_command("seed_core")
        assert Permission.objects.count() == 52

    def test_creates_80_role_templates(self):
        """8 roles x 10 industries = 80 templates."""
        call_command("seed_core")
        assert IndustryRoleTemplate.objects.count() == 80

    def test_creates_50_users(self):
        """5 users per company x 10 companies = 50."""
        call_command("seed_core")
        assert User.objects.count() == 50

    def test_each_company_has_admin_user(self):
        call_command("seed_core")
        for company in Company.objects.all():
            admin_profile = UserProfile.objects.filter(
                company=company, is_company_admin=True,
            )
            assert admin_profile.exists(), f"{company.name} missing admin"

    def test_provisions_roles_for_each_company(self):
        call_command("seed_core")
        for company in Company.objects.all():
            roles = Role.objects.filter(company=company)
            assert roles.count() == 8, f"{company.name} has {roles.count()} roles"

    def test_idempotent(self):
        call_command("seed_core")
        call_command("seed_core")
        assert Company.objects.count() == 10
        assert User.objects.count() == 50
        assert IndustryRoleTemplate.objects.count() == 80

    def test_novapay_brand_color(self):
        call_command("seed_core")
        novapay = Company.objects.get(slug="novapay")
        assert novapay.brand_color == "#2563EB"
        assert novapay.industry == "fintech"

    def test_users_can_authenticate(self):
        call_command("seed_core")
        user = User.objects.get(username="novapay_admin")
        assert user.check_password("admin")
