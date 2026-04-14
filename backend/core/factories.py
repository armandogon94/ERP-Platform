import factory
from django.contrib.auth.models import User

from core.models import (
    Company,
    Industry,
    IndustryConfigTemplate,
    IndustryRoleTemplate,
    Permission,
    Role,
    RoleLevel,
    UserProfile,
)


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: f"Company {n}")
    slug = factory.Sequence(lambda n: f"company-{n}")
    brand_color = "#714B67"
    industry = Industry.FINTECH
    is_active = True
    config_json = factory.LazyFunction(dict)


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(
        "core.factories.UserFactory",
        profile=None,  # prevent recursion
    )
    company = factory.SubFactory(CompanyFactory)
    is_company_admin = False


class UserFactory(factory.django.DjangoModelFactory):
    """Creates a Django User with an associated UserProfile."""

    class Meta:
        model = User
        exclude = ["company", "is_admin"]
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    # Passed through to profile creation
    company = factory.SubFactory(CompanyFactory)
    is_admin = False

    profile = factory.RelatedFactory(
        UserProfileFactory,
        factory_related_name="user",
        company=factory.SelfAttribute("..company"),
        is_company_admin=factory.SelfAttribute("..is_admin"),
    )

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save the instance after post-generation hooks (password, profile)."""
        if create:
            instance.set_password("testpass123")
            instance.save()


class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission
        django_get_or_create = ["codename"]

    codename = factory.Sequence(lambda n: f"module{n}.read")
    name = factory.LazyAttribute(lambda o: f"Can {o.codename}")
    module = factory.LazyAttribute(lambda o: o.codename.split(".")[0])
    action = factory.LazyAttribute(lambda o: o.codename.split(".")[1])


class IndustryConfigTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IndustryConfigTemplate
        django_get_or_create = ["industry"]

    industry = Industry.FINTECH
    config = factory.LazyFunction(dict)


class IndustryRoleTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IndustryRoleTemplate
        django_get_or_create = ["industry", "role_slug"]

    industry = Industry.FINTECH
    role_slug = factory.Sequence(lambda n: f"role-{n}")
    role_name = factory.LazyAttribute(lambda o: o.role_slug.replace("-", " ").title())
    role_level = RoleLevel.OPERATIONAL
    module_permissions = factory.LazyFunction(list)
    dashboard_config = factory.LazyFunction(dict)
    anomaly_alerts = factory.LazyFunction(list)


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Role {n}")
    role_level = RoleLevel.OPERATIONAL
    is_system = False
