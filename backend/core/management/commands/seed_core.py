from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import (
    Company,
    Industry,
    IndustryRoleTemplate,
    Permission,
    RoleLevel,
    UserProfile,
)
from core.services.company_provisioning import provision_company_roles

# 10 companies with their industry + brand color
COMPANIES = [
    {"name": "NovaPay", "slug": "novapay", "industry": Industry.FINTECH, "brand_color": "#2563EB"},
    {"name": "MedVista", "slug": "medvista", "industry": Industry.HEALTHCARE, "brand_color": "#059669"},
    {"name": "TrustGuard", "slug": "trustguard", "industry": Industry.INSURANCE, "brand_color": "#1E3A5F"},
    {"name": "UrbanNest", "slug": "urbannest", "industry": Industry.REAL_ESTATE, "brand_color": "#D97706"},
    {"name": "SwiftRoute", "slug": "swiftroute", "industry": Industry.LOGISTICS, "brand_color": "#7C3AED"},
    {"name": "DentaFlow", "slug": "dentaflow", "industry": Industry.DENTAL, "brand_color": "#06B6D4"},
    {"name": "JurisPath", "slug": "jurispath", "industry": Industry.LEGAL, "brand_color": "#166534"},
    {"name": "TableSync", "slug": "tablesync", "industry": Industry.HOSPITALITY, "brand_color": "#9F1239"},
    {"name": "CraneStack", "slug": "cranestack", "industry": Industry.CONSTRUCTION, "brand_color": "#EA580C"},
    {"name": "EduPulse", "slug": "edupulse", "industry": Industry.EDUCATION, "brand_color": "#6D28D9"},
]

# 13 modules available for each company
MODULES = [
    "accounting", "invoicing", "inventory", "fleet", "calendar",
    "hr", "projects", "purchasing", "sales", "manufacturing",
    "pos", "helpdesk", "reports",
]

# Standard permissions per module
ACTIONS = ["read", "create", "update", "delete"]

# 8 role templates per industry (80 total)
# Each industry has roles matching real job responsibilities
ROLE_TEMPLATES = {
    Industry.FINTECH: [
        ("cfo", "Chief Financial Officer", RoleLevel.EXECUTIVE, MODULES),
        ("compliance-officer", "Compliance Officer", RoleLevel.DIRECTOR, ["accounting", "invoicing", "reports", "helpdesk"]),
        ("finance-manager", "Finance Manager", RoleLevel.MANAGER, ["accounting", "invoicing", "purchasing", "reports"]),
        ("accountant", "Accountant", RoleLevel.SUPERVISOR, ["accounting", "invoicing"]),
        ("financial-analyst", "Financial Analyst", RoleLevel.SUPERVISOR, ["accounting", "reports"]),
        ("treasury-specialist", "Treasury Specialist", RoleLevel.OPERATIONAL, ["accounting"]),
        ("billing-clerk", "Billing Clerk", RoleLevel.OPERATIONAL, ["invoicing"]),
        ("support-agent", "Customer Support Agent", RoleLevel.OPERATIONAL, ["helpdesk"]),
    ],
    Industry.HEALTHCARE: [
        ("medical-director", "Medical Director", RoleLevel.EXECUTIVE, MODULES),
        ("practice-manager", "Practice Manager", RoleLevel.DIRECTOR, ["hr", "accounting", "invoicing", "inventory", "calendar", "reports"]),
        ("head-nurse", "Head Nurse", RoleLevel.MANAGER, ["hr", "calendar", "inventory", "helpdesk"]),
        ("physician", "Physician", RoleLevel.SUPERVISOR, ["calendar", "projects", "helpdesk"]),
        ("pharmacist", "Pharmacist", RoleLevel.SUPERVISOR, ["inventory", "purchasing"]),
        ("receptionist", "Receptionist", RoleLevel.OPERATIONAL, ["calendar", "helpdesk"]),
        ("medical-biller", "Medical Biller", RoleLevel.OPERATIONAL, ["invoicing", "accounting"]),
        ("lab-technician", "Lab Technician", RoleLevel.OPERATIONAL, ["inventory"]),
    ],
    Industry.INSURANCE: [
        ("ceo", "Chief Executive Officer", RoleLevel.EXECUTIVE, MODULES),
        ("underwriting-manager", "Underwriting Manager", RoleLevel.DIRECTOR, ["sales", "accounting", "reports"]),
        ("claims-manager", "Claims Manager", RoleLevel.MANAGER, ["helpdesk", "accounting", "invoicing"]),
        ("senior-underwriter", "Senior Underwriter", RoleLevel.SUPERVISOR, ["sales", "reports"]),
        ("claims-adjuster", "Claims Adjuster", RoleLevel.SUPERVISOR, ["helpdesk"]),
        ("policy-admin", "Policy Administrator", RoleLevel.OPERATIONAL, ["sales", "invoicing"]),
        ("accountant", "Accountant", RoleLevel.OPERATIONAL, ["accounting", "invoicing"]),
        ("customer-service", "Customer Service Rep", RoleLevel.OPERATIONAL, ["helpdesk"]),
    ],
    Industry.REAL_ESTATE: [
        ("broker", "Managing Broker", RoleLevel.EXECUTIVE, MODULES),
        ("sales-director", "Sales Director", RoleLevel.DIRECTOR, ["sales", "invoicing", "projects", "reports"]),
        ("property-manager", "Property Manager", RoleLevel.MANAGER, ["projects", "fleet", "helpdesk", "accounting"]),
        ("senior-agent", "Senior Real Estate Agent", RoleLevel.SUPERVISOR, ["sales", "calendar"]),
        ("leasing-agent", "Leasing Agent", RoleLevel.SUPERVISOR, ["sales", "calendar", "invoicing"]),
        ("agent", "Real Estate Agent", RoleLevel.OPERATIONAL, ["sales", "calendar"]),
        ("maintenance-coord", "Maintenance Coordinator", RoleLevel.OPERATIONAL, ["helpdesk", "inventory"]),
        ("admin-assistant", "Administrative Assistant", RoleLevel.OPERATIONAL, ["calendar", "helpdesk"]),
    ],
    Industry.LOGISTICS: [
        ("vp-operations", "VP of Operations", RoleLevel.EXECUTIVE, MODULES),
        ("logistics-manager", "Logistics Manager", RoleLevel.DIRECTOR, ["inventory", "fleet", "purchasing", "reports"]),
        ("warehouse-manager", "Warehouse Manager", RoleLevel.MANAGER, ["inventory", "purchasing", "manufacturing"]),
        ("fleet-manager", "Fleet Manager", RoleLevel.SUPERVISOR, ["fleet", "hr"]),
        ("dispatch-supervisor", "Dispatch Supervisor", RoleLevel.SUPERVISOR, ["fleet", "calendar"]),
        ("warehouse-worker", "Warehouse Associate", RoleLevel.OPERATIONAL, ["inventory"]),
        ("driver", "Delivery Driver", RoleLevel.OPERATIONAL, ["fleet"]),
        ("procurement-clerk", "Procurement Clerk", RoleLevel.OPERATIONAL, ["purchasing"]),
    ],
    Industry.DENTAL: [
        ("practice-owner", "Practice Owner", RoleLevel.EXECUTIVE, MODULES),
        ("office-manager", "Office Manager", RoleLevel.DIRECTOR, ["hr", "accounting", "invoicing", "inventory", "calendar", "reports"]),
        ("lead-dentist", "Lead Dentist", RoleLevel.MANAGER, ["calendar", "projects", "inventory"]),
        ("dentist", "Dentist", RoleLevel.SUPERVISOR, ["calendar", "inventory"]),
        ("hygienist", "Dental Hygienist", RoleLevel.SUPERVISOR, ["calendar"]),
        ("dental-assistant", "Dental Assistant", RoleLevel.OPERATIONAL, ["calendar", "inventory"]),
        ("front-desk", "Front Desk Coordinator", RoleLevel.OPERATIONAL, ["calendar", "invoicing", "helpdesk"]),
        ("billing-specialist", "Billing Specialist", RoleLevel.OPERATIONAL, ["invoicing", "accounting"]),
    ],
    Industry.LEGAL: [
        ("managing-partner", "Managing Partner", RoleLevel.EXECUTIVE, MODULES),
        ("senior-partner", "Senior Partner", RoleLevel.DIRECTOR, ["projects", "accounting", "invoicing", "hr", "reports"]),
        ("associate", "Associate Attorney", RoleLevel.MANAGER, ["projects", "calendar", "invoicing"]),
        ("paralegal-manager", "Paralegal Manager", RoleLevel.SUPERVISOR, ["projects", "calendar", "helpdesk"]),
        ("paralegal", "Paralegal", RoleLevel.SUPERVISOR, ["projects", "calendar"]),
        ("legal-secretary", "Legal Secretary", RoleLevel.OPERATIONAL, ["calendar", "helpdesk"]),
        ("billing-manager", "Billing Manager", RoleLevel.OPERATIONAL, ["invoicing", "accounting"]),
        ("receptionist", "Receptionist", RoleLevel.OPERATIONAL, ["calendar", "helpdesk"]),
    ],
    Industry.HOSPITALITY: [
        ("gm", "General Manager", RoleLevel.EXECUTIVE, MODULES),
        ("operations-manager", "Operations Manager", RoleLevel.DIRECTOR, ["inventory", "purchasing", "hr", "manufacturing", "reports"]),
        ("head-chef", "Head Chef", RoleLevel.MANAGER, ["inventory", "purchasing", "manufacturing"]),
        ("floor-manager", "Floor Manager", RoleLevel.SUPERVISOR, ["pos", "hr", "calendar"]),
        ("sous-chef", "Sous Chef", RoleLevel.SUPERVISOR, ["inventory", "manufacturing"]),
        ("bartender", "Lead Bartender", RoleLevel.OPERATIONAL, ["pos", "inventory"]),
        ("server", "Server", RoleLevel.OPERATIONAL, ["pos"]),
        ("host", "Host/Hostess", RoleLevel.OPERATIONAL, ["calendar", "pos"]),
    ],
    Industry.CONSTRUCTION: [
        ("ceo", "Chief Executive Officer", RoleLevel.EXECUTIVE, MODULES),
        ("project-director", "Project Director", RoleLevel.DIRECTOR, ["projects", "purchasing", "hr", "fleet", "reports"]),
        ("site-manager", "Site Manager", RoleLevel.MANAGER, ["projects", "inventory", "hr", "fleet"]),
        ("project-engineer", "Project Engineer", RoleLevel.SUPERVISOR, ["projects", "inventory"]),
        ("safety-officer", "Safety Officer", RoleLevel.SUPERVISOR, ["hr", "helpdesk"]),
        ("estimator", "Estimator", RoleLevel.OPERATIONAL, ["projects", "purchasing"]),
        ("foreman", "Foreman", RoleLevel.OPERATIONAL, ["projects", "hr"]),
        ("equipment-operator", "Equipment Operator", RoleLevel.OPERATIONAL, ["fleet"]),
    ],
    Industry.EDUCATION: [
        ("principal", "Principal/Director", RoleLevel.EXECUTIVE, MODULES),
        ("vice-principal", "Vice Principal", RoleLevel.DIRECTOR, ["hr", "calendar", "projects", "reports"]),
        ("department-head", "Department Head", RoleLevel.MANAGER, ["hr", "calendar", "projects", "inventory"]),
        ("teacher", "Teacher", RoleLevel.SUPERVISOR, ["calendar", "projects"]),
        ("counselor", "Guidance Counselor", RoleLevel.SUPERVISOR, ["calendar", "helpdesk"]),
        ("registrar", "Registrar", RoleLevel.OPERATIONAL, ["hr", "calendar"]),
        ("librarian", "Librarian", RoleLevel.OPERATIONAL, ["inventory"]),
        ("admin-staff", "Administrative Staff", RoleLevel.OPERATIONAL, ["calendar", "helpdesk"]),
    ],
}


class Command(BaseCommand):
    help = "Seed 10 companies, 50 users (5 per company), permissions, and 80 industry role templates"

    def handle(self, *args, **options):
        self._seed_permissions()
        self._seed_role_templates()
        self._seed_companies()
        self.stdout.write(self.style.SUCCESS("Core seed data loaded."))

    def _seed_permissions(self):
        count = 0
        for module in MODULES:
            for action in ACTIONS:
                _, created = Permission.objects.get_or_create(
                    codename=f"{module}.{action}",
                    defaults={"module": module, "action": action},
                )
                if created:
                    count += 1
        self.stdout.write(f"  Permissions: {count} created")

    def _seed_role_templates(self):
        count = 0
        for industry, roles in ROLE_TEMPLATES.items():
            for slug, name, level, modules in roles:
                perms = []
                for mod in modules:
                    for act in ACTIONS:
                        perms.append(f"{mod}.{act}")

                _, created = IndustryRoleTemplate.objects.get_or_create(
                    industry=industry,
                    role_slug=slug,
                    defaults={
                        "role_name": name,
                        "role_level": level,
                        "module_permissions": perms,
                    },
                )
                if created:
                    count += 1
        self.stdout.write(f"  Role templates: {count} created")

    def _seed_companies(self):
        for company_data in COMPANIES:
            company, created = Company.objects.get_or_create(
                slug=company_data["slug"],
                defaults={
                    "name": company_data["name"],
                    "brand_color": company_data["brand_color"],
                    "industry": company_data["industry"],
                },
            )
            if created:
                self.stdout.write(f"  Company: {company.name}")

            # Provision roles from templates
            roles = provision_company_roles(company)
            if roles:
                self.stdout.write(f"    Provisioned {len(roles)} roles")

            # Create 5 users per company
            self._seed_company_users(company)

    def _seed_company_users(self, company):
        slug = company.slug
        users_config = [
            {"username": f"{slug}_admin", "email": f"admin@{slug}.com", "first_name": "Admin", "is_admin": True},
            {"username": f"{slug}_manager", "email": f"manager@{slug}.com", "first_name": "Manager", "is_admin": False},
            {"username": f"{slug}_user1", "email": f"user1@{slug}.com", "first_name": "User One", "is_admin": False},
            {"username": f"{slug}_user2", "email": f"user2@{slug}.com", "first_name": "User Two", "is_admin": False},
            {"username": f"{slug}_user3", "email": f"user3@{slug}.com", "first_name": "User Three", "is_admin": False},
        ]

        for cfg in users_config:
            user, created = User.objects.get_or_create(
                username=cfg["username"],
                defaults={
                    "email": cfg["email"],
                    "first_name": cfg["first_name"],
                    "last_name": company.name,
                },
            )
            if created:
                user.set_password("admin")
                user.save()

                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "company": company,
                        "is_company_admin": cfg["is_admin"],
                    },
                )
