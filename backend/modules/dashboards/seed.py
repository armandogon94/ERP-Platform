"""Seed a company's default dashboard from its industry YAML preset.

The preset file is selected by ``company.industry``; if no file matches,
we fall back to ``generic.yaml`` so every tenant still gets a working
dashboard on first login.
"""

from __future__ import annotations

from pathlib import Path

import yaml

PRESETS_DIR = Path(__file__).resolve().parent / "industry_presets"


def _preset_path(industry: str) -> Path:
    path = PRESETS_DIR / f"{industry}.yaml"
    if path.exists():
        return path
    return PRESETS_DIR / "generic.yaml"


def _load_preset(industry: str) -> dict:
    with open(_preset_path(industry)) as fh:
        return yaml.safe_load(fh) or {}


def seed_default_dashboard(company, target=None):
    """Create (or repopulate) the default dashboard for ``company``.

    If ``target`` is provided, widgets are added to that existing Dashboard
    row; otherwise a new Dashboard is created.
    """
    from modules.dashboards.models import Dashboard, DashboardWidget

    preset = _load_preset(company.industry)
    default_cfg = next(
        (d for d in preset.get("dashboards", []) if d.get("is_default")),
        None,
    )
    if default_cfg is None and preset.get("dashboards"):
        default_cfg = preset["dashboards"][0]

    if default_cfg is None:
        # Truly empty preset — nothing to seed.
        return None

    if target is None:
        dashboard, _ = Dashboard.objects.get_or_create(
            company=company,
            slug=default_cfg.get("slug", "home"),
            defaults={
                "name": default_cfg.get("name", "Home"),
                "is_default": True,
                "industry_preset": company.industry,
            },
        )
    else:
        dashboard = target

    for idx, w in enumerate(default_cfg.get("widgets", [])):
        DashboardWidget.objects.create(
            company=company,
            dashboard=dashboard,
            position=w.get("position", idx),
            widget_type=w.get("widget_type", "kpi"),
            title=w.get("title", "Widget"),
            subtitle=w.get("subtitle", ""),
            data_source=w["data_source"],
            config_json=w.get("config", {}),
        )

    return dashboard
