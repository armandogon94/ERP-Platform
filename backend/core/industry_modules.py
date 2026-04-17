"""Industry → module subset mapping used by `seed_industry_demo` (D26).

Derived from `INDUSTRY-BRANDING-CONTEXT.md`. Each industry's tuple lists
the *module slugs* that `seed_industry_demo --company <slug>` will seed
for that company. A "base" tuple applies to every industry.

Slugs map 1:1 to `manage.py seed_<module>_demo` commands.
"""

# Every industry gets these baseline modules seeded.
BASE_MODULES: tuple[str, ...] = (
    "hr",
    "calendar",
    "partners",  # not a command yet, but reserved
)

INDUSTRY_MODULES: dict[str, tuple[str, ...]] = {
    "fintech": ("accounting", "invoicing", "sales", "reports"),
    "healthcare": ("calendar", "hr", "invoicing", "helpdesk"),
    "insurance": ("sales", "accounting", "helpdesk", "reports"),
    "real_estate": ("sales", "calendar", "projects"),
    "logistics": ("fleet", "inventory", "purchasing", "reports"),
    "dental": ("calendar", "inventory", "invoicing", "helpdesk"),
    "legal": ("invoicing", "projects", "hr"),
    "hospitality": ("inventory", "manufacturing", "pos", "helpdesk"),
    "construction": ("projects", "purchasing", "fleet", "manufacturing", "hr"),
    "education": ("calendar", "hr", "invoicing", "sales"),
}


def modules_for_industry(industry: str) -> tuple[str, ...]:
    """Return the unique ordered tuple of module slugs to seed for an industry."""
    extras = INDUSTRY_MODULES.get(industry, ())
    seen: set[str] = set()
    ordered: list[str] = []
    for m in BASE_MODULES + extras:
        if m not in seen:
            seen.add(m)
            ordered.append(m)
    return tuple(ordered)
