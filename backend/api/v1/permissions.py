from rest_framework.permissions import BasePermission


class IsCompanyMember(BasePermission):
    """Verifies user belongs to a company (has a UserProfile)."""

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.company
        )


class IsCompanyAdmin(BasePermission):
    """Verifies user is a company admin."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.is_company_admin
        )


class ModulePermission(BasePermission):
    """Checks module-level + action-level permission.

    Usage on a ViewSet:
        permission_classes = [IsCompanyMember, ModulePermission]
        module_name = "accounting"

    Maps HTTP method to action:
        GET    → {module}.read
        POST   → {module}.create
        PUT    → {module}.update
        PATCH  → {module}.update
        DELETE → {module}.delete
    """

    METHOD_ACTION_MAP = {
        "GET": "read",
        "HEAD": "read",
        "OPTIONS": "read",
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        module_name = getattr(view, "module_name", None)
        if module_name is None:
            return True

        action = self.METHOD_ACTION_MAP.get(request.method, "read")
        required_perm = f"{module_name}.{action}"

        return required_perm in request.permissions
