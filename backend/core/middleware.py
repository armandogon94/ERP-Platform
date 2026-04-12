from django.utils.functional import SimpleLazyObject

from core.models import RoleLevel


def _get_company_context(user):
    """Resolve company, roles, and permissions for an authenticated user."""
    if not user.is_authenticated:
        return None

    try:
        profile = user.profile
    except Exception:
        return None

    company = profile.company

    user_roles = (
        user.user_roles.select_related("role")
        .prefetch_related("role__permissions")
        .filter(role__deleted_at__isnull=True)
    )

    roles = [ur.role for ur in user_roles]
    permissions = set()
    dashboard_config = {}
    max_level = None

    for role in roles:
        for perm in role.permissions.all():
            permissions.add(perm.codename)
        if role.dashboard_config:
            dashboard_config.update(role.dashboard_config)
        if max_level is None or role.role_level > max_level:
            max_level = role.role_level

    return {
        "company": company,
        "company_id": company.pk,
        "roles": roles,
        "permissions": permissions,
        "role_level": max_level or RoleLevel.OPERATIONAL,
        "dashboard_config": dashboard_config,
        "is_company_admin": profile.is_company_admin,
    }


class CompanyRoleContextMiddleware:
    """Injects company and RBAC context into every request.

    After authentication, sets:
    - request.company
    - request.company_id
    - request.roles
    - request.permissions (set of codenames)
    - request.role_level
    - request.dashboard_config
    - request.is_company_admin
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Use lazy evaluation to avoid DB queries for unauthenticated requests
        def _resolve():
            return _get_company_context(request.user)

        context = SimpleLazyObject(_resolve)

        request.company = SimpleLazyObject(
            lambda: context["company"] if context else None
        )
        request.company_id = SimpleLazyObject(
            lambda: context["company_id"] if context else None
        )
        request.roles = SimpleLazyObject(
            lambda: context["roles"] if context else []
        )
        request.permissions = SimpleLazyObject(
            lambda: context["permissions"] if context else set()
        )
        request.role_level = SimpleLazyObject(
            lambda: context["role_level"] if context else None
        )
        request.dashboard_config = SimpleLazyObject(
            lambda: context["dashboard_config"] if context else {}
        )
        request.is_company_admin = SimpleLazyObject(
            lambda: context["is_company_admin"] if context else False
        )

        return self.get_response(request)
