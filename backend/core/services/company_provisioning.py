from core.models import (
    IndustryRoleTemplate,
    Permission,
    Role,
    RolePermission,
)


def provision_company_roles(company):
    """Copy IndustryRoleTemplates into company-specific Roles.

    For each template matching the company's industry:
    1. Create a Role linked to the template
    2. Resolve module_permissions JSON into RolePermission records
    """
    templates = IndustryRoleTemplate.objects.filter(industry=company.industry)
    created_roles = []

    for template in templates:
        role, _ = Role.all_objects.get_or_create(
            company=company,
            name=template.role_name,
            defaults={
                "description": f"System role from {template.get_industry_display()} template",
                "is_system": True,
                "role_level": template.role_level,
                "template": template,
                "dashboard_config": template.dashboard_config,
                "anomaly_alerts": template.anomaly_alerts,
            },
        )

        # Resolve permission codenames from template JSON
        for codename in template.module_permissions:
            try:
                perm = Permission.objects.get(codename=codename)
                RolePermission.objects.get_or_create(role=role, permission=perm)
            except Permission.DoesNotExist:
                pass

        created_roles.append(role)

    return created_roles
