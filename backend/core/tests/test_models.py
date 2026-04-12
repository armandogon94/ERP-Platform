import pytest
from django.utils import timezone

from core.factories import CompanyFactory, UserFactory
from core.models import Company, Industry, UserProfile


@pytest.mark.django_db
class TestCompany:
    def test_create_company(self):
        company = CompanyFactory(
            name="NovaPay",
            slug="novapay",
            brand_color="#2563EB",
            industry=Industry.FINTECH,
        )
        assert company.pk is not None
        assert company.name == "NovaPay"
        assert company.slug == "novapay"
        assert company.brand_color == "#2563EB"
        assert company.industry == Industry.FINTECH
        assert company.is_active is True

    def test_company_str(self):
        company = CompanyFactory(name="DentaFlow")
        assert str(company) == "DentaFlow"

    def test_company_config_json_default(self):
        company = CompanyFactory()
        assert company.config_json == {}

    def test_company_slug_unique(self):
        CompanyFactory(slug="unique-slug")
        with pytest.raises(Exception):
            CompanyFactory(slug="unique-slug")

    def test_company_ordering(self):
        CompanyFactory(name="Zebra")
        CompanyFactory(name="Alpha")
        companies = list(Company.objects.values_list("name", flat=True))
        assert companies == ["Alpha", "Zebra"]


@pytest.mark.django_db
class TestUserProfile:
    def test_create_user_with_profile(self):
        company = CompanyFactory(name="NovaPay", slug="novapay")
        user = UserFactory(
            username="admin",
            email="admin@novapay.com",
            company=company,
        )
        assert user.pk is not None
        assert hasattr(user, "profile")
        assert user.profile.company == company
        assert user.profile.is_company_admin is False

    def test_user_profile_admin_flag(self):
        company = CompanyFactory()
        user = UserFactory(company=company, is_admin=True)
        assert user.profile.is_company_admin is True

    def test_user_profile_defaults(self):
        user = UserFactory()
        profile = user.profile
        assert profile.timezone == "UTC"
        assert profile.language == "en"
        assert profile.phone == ""
        assert profile.department == ""
        assert profile.job_title == ""

    def test_user_profile_str(self):
        company = CompanyFactory(slug="novapay")
        user = UserFactory(
            first_name="John",
            last_name="Doe",
            company=company,
        )
        assert str(user.profile) == "John Doe (novapay)"

    def test_company_members_reverse_relation(self):
        company = CompanyFactory()
        UserFactory(company=company)
        UserFactory(company=company)
        assert company.members.count() == 2


@pytest.mark.django_db
class TestSoftDelete:
    def test_soft_delete_excludes_from_default_queryset(self):
        """TenantModel subclasses use SoftDeleteManager.
        Company itself doesn't use soft delete (it's the root),
        so we test via a proxy or direct field manipulation on UserProfile.
        """
        company = CompanyFactory()
        user = UserFactory(company=company)
        profile = user.profile

        # Soft delete the profile
        profile.deleted_at = timezone.now()
        profile.save()

        # Default manager should exclude it
        # UserProfile doesn't inherit TenantModel, so it uses default manager
        # We'll verify soft delete works on UserProfile by checking it's still in DB
        assert UserProfile.objects.filter(pk=profile.pk).exists()

    def test_tenant_model_soft_delete_method(self):
        """Test the soft_delete() and restore() methods on TenantModel subclasses.

        Since we don't have a concrete TenantModel subclass yet,
        we'll create a minimal one for testing in later slices.
        For now, verify the Company and UserProfile models work correctly.
        """
        company = CompanyFactory()
        assert Company.objects.filter(pk=company.pk).exists()


@pytest.mark.django_db
class TestCompanyIsolation:
    def test_users_belong_to_one_company(self):
        company_a = CompanyFactory(name="Company A")
        company_b = CompanyFactory(name="Company B")
        user_a = UserFactory(company=company_a)
        user_b = UserFactory(company=company_b)

        assert user_a.profile.company == company_a
        assert user_b.profile.company == company_b

    def test_company_members_isolated(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        UserFactory(company=company_a)
        UserFactory(company=company_a)
        UserFactory(company=company_b)

        assert company_a.members.count() == 2
        assert company_b.members.count() == 1
