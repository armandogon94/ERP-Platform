"""Industry Config Service — 3-tier configuration hierarchy.

Resolution order (most specific wins):
  1. ModuleConfig records (company + module level)
  2. Company.config_json (company-level overrides)
  3. IndustryConfigTemplate.config (industry defaults from YAML)

Public API:
  merge_configs(base, override)      — deep merge, override wins, lists replaced
  get_industry_config(industry)      — tier 3: raw industry template config
  get_company_config(company)        — tiers 3+2 merged
  get_resolved_config(company, module_name=None)  — full 3-tier merge, cached
  get_terminology(company)           — shortcut for config["terminology"]
  invalidate_company_config(company_id)  — delete all cache keys for a company
  invalidate_industry_config(industry)   — delete cache keys for all companies
"""

from __future__ import annotations

import copy
import logging
from typing import TYPE_CHECKING

from django.core.cache import cache

if TYPE_CHECKING:
    from core.models import Company

logger = logging.getLogger(__name__)

CACHE_TTL = 300  # seconds


def merge_configs(base: dict, override: dict) -> dict:
    """Deep-merge two config dicts. Override wins on conflicts.

    Lists are replaced wholesale (not appended). Dicts are recursively merged.
    Neither input dict is mutated.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def get_industry_config(industry: str) -> dict:
    """Return the raw config for an industry, or {} if no template exists."""
    from core.models import IndustryConfigTemplate

    try:
        template = IndustryConfigTemplate.objects.get(industry=industry)
        return template.config or {}
    except IndustryConfigTemplate.DoesNotExist:
        return {}


def get_company_config(company: "Company") -> dict:
    """Return the 2-tier merged config: industry defaults + company overrides."""
    industry_config = get_industry_config(company.industry)
    company_overrides = company.config_json or {}
    return merge_configs(industry_config, company_overrides)


def get_resolved_config(company: "Company", module_name: str | None = None) -> dict:
    """Return the fully resolved 3-tier config for a company (Redis-cached).

    If module_name is provided, ModuleConfig records for that module are folded
    into the config under config["modules"][module_name].
    """
    cache_key = _cache_key(company.id, module_name)

    try:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    except Exception:
        logger.warning("Cache read failed for key %s — falling back to DB", cache_key)

    config = get_company_config(company)

    if module_name:
        config = _apply_module_config(config, company, module_name)

    try:
        cache.set(cache_key, config, timeout=CACHE_TTL)
    except Exception:
        logger.warning("Cache write failed for key %s", cache_key)

    return config


def invalidate_company_config(company_id: int) -> None:
    """Delete all cached config entries for a given company."""
    # Delete the global key and any per-module keys by using a pattern approach.
    # Since Django's LocMemCache/RedisCache both support delete_many with exact keys,
    # we use a stored set of known module names or just clear the patterns we know about.
    # For simplicity: we delete the global key and use cache.delete_pattern if available,
    # otherwise we scan known module names.
    _delete_cache_key(_cache_key(company_id, None))
    for module_name in _get_known_module_names(company_id):
        _delete_cache_key(_cache_key(company_id, module_name))


def invalidate_industry_config(industry: str) -> None:
    """Delete cached config for all companies that belong to this industry."""
    from core.models import Company

    company_ids = Company.objects.filter(industry=industry).values_list("id", flat=True)
    for company_id in company_ids:
        invalidate_company_config(company_id)


def get_terminology(company: "Company") -> dict:
    """Shortcut — return the terminology sub-dict from resolved company config."""
    config = get_company_config(company)
    return config.get("terminology", {})


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _apply_module_config(config: dict, company: "Company", module_name: str) -> dict:
    """Fold ModuleConfig key-value records into config["modules"][module_name]."""
    from core.models import ModuleConfig, ModuleRegistry

    try:
        module = ModuleRegistry.objects.get(company=company, name=module_name)
    except ModuleRegistry.DoesNotExist:
        return config

    module_configs = ModuleConfig.objects.filter(
        company=company,
        module=module,
        deleted_at__isnull=True,
    )

    if not module_configs.exists():
        return config

    # Build overrides dict from ModuleConfig records
    module_overrides: dict = {}
    for mc in module_configs:
        module_overrides[mc.key] = _cast_value(mc.value, mc.value_type)

    # Merge into config["modules"][module_name]
    modules = copy.deepcopy(config.get("modules", {}))
    existing_module_config = modules.get(module_name, {})
    modules[module_name] = merge_configs(existing_module_config, module_overrides)

    result = copy.deepcopy(config)
    result["modules"] = modules
    return result


def _cast_value(value: str, value_type: str):
    """Cast a string ModuleConfig value to its declared Python type."""
    import json

    if value_type == "int":
        return int(value)
    if value_type == "bool":
        return value.lower() in ("true", "1", "yes")
    if value_type == "json":
        return json.loads(value)
    return value  # string


def _cache_key(company_id: int, module_name: str | None) -> str:
    """Build the Redis cache key for a company + optional module."""
    module_part = module_name if module_name else "__global__"
    return f"config:{company_id}:{module_part}"


def _delete_cache_key(key: str) -> None:
    """Delete a single cache key, swallowing errors gracefully."""
    try:
        cache.delete(key)
    except Exception:
        logger.warning("Cache delete failed for key %s", key)


def _get_known_module_names(company_id: int) -> list[str]:
    """Return the set of module names that might have cached entries for this company."""
    from core.models import ModuleRegistry

    return list(
        ModuleRegistry.objects.filter(company_id=company_id).values_list("name", flat=True)
    )
