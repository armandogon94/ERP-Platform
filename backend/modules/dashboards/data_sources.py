"""Data source registry for dashboard widgets.

Every widget references a **named data source** from this registry — never
raw SQL from the client. Each source is a pure function that takes the
tenant's company + kwargs and returns a shape matching the widget type it
feeds.

Shapes by widget type:
* ``kpi`` → ``{"value": "<str>", "detail": "<optional str>"}``
* ``bar`` / ``line`` / ``area`` → ``[{"group": str, "value": number}, ...]``
* ``pie`` → ``[{"group": str, "value": number}, ...]``
* ``table`` → ``[{"col_a": ..., "col_b": ...}, ...]`` + optional columns list

Per-company results are cached for 5 minutes (see ``compute_data_source``)
so opening a dashboard 3 times in a minute = 1 DB hit, not 3N.

Upgrade path: when a specific source becomes expensive (>~100ms), replace
its implementation with a Postgres ``MATERIALIZED VIEW`` refreshed by a
Celery Beat schedule. The registry key stays the same, so widgets don't
change.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Callable

from django.core.cache import cache
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from django.utils import timezone

_REGISTRY: dict[str, Callable] = {}


def register_data_source(key: str):
    """Decorator to register a data source function under ``key``.

    Source functions receive ``(company, **config)`` and return JSON-safe data.
    """

    def wrap(fn: Callable) -> Callable:
        if key in _REGISTRY:
            raise RuntimeError(f"Data source {key!r} already registered.")
        _REGISTRY[key] = fn
        return fn

    return wrap


def compute_data_source(key: str, company, config: dict | None = None):
    """Look up + call a registered data source. Cached per (company, key, config)."""
    if key not in _REGISTRY:
        raise KeyError(f"Unknown data source {key!r}")

    config = config or {}
    cache_key = f"widget:{company.id}:{key}:{_stable_hash(config)}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    fn = _REGISTRY[key]
    result = _serialize(fn(company, **config))
    cache.set(cache_key, result, timeout=300)  # 5 min
    return result


def list_data_sources() -> list[str]:
    """Useful for diagnostics / admin."""
    return sorted(_REGISTRY.keys())


# ─── helpers ────────────────────────────────────────────────────────────


def _stable_hash(config: dict) -> str:
    """Short deterministic hash — Memcached-safe (no colons or spaces)."""
    import hashlib
    import json

    payload = json.dumps(config, sort_keys=True, default=str)
    return hashlib.md5(payload.encode()).hexdigest()[:12]


def _serialize(value):
    """Convert Decimal + datetime values to JSON-safe primitives."""
    from datetime import date, datetime

    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(v) for v in value]
    return value


def _period_start(period: str):
    """Resolve a friendly period name to a start datetime."""
    now = timezone.now()
    if period == "last_7_days":
        return now - timedelta(days=7)
    if period == "last_30_days":
        return now - timedelta(days=30)
    if period == "last_90_days":
        return now - timedelta(days=90)
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "this_month":
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if period == "this_year":
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    # default: last 30 days
    return now - timedelta(days=30)


# ────────────────────────────────────────────────────────────────────────
# Invoicing
# ────────────────────────────────────────────────────────────────────────


@register_data_source("invoicing.outstanding_total")
def invoicing_outstanding_total(company, **_):
    from modules.invoicing.models import Invoice

    agg = Invoice.objects.filter(company=company, status="posted").aggregate(
        total=Sum("total_amount"), count=Count("id")
    )
    return {
        "value": f"${agg['total'] or 0:,.2f}",
        "detail": f"{agg['count'] or 0} invoice(s)",
    }


@register_data_source("invoicing.revenue_daily")
def invoicing_revenue_daily(company, period: str = "last_30_days", **_):
    from modules.invoicing.models import Invoice

    start = _period_start(period)
    rows = (
        Invoice.objects.filter(
            company=company,
            status__in=["posted", "paid"],
            invoice_date__gte=start.date(),
        )
        .annotate(day=TruncDay("invoice_date"))
        .values("day")
        .annotate(value=Sum("total_amount"))
        .order_by("day")
    )
    return [
        {"group": r["day"].isoformat() if r["day"] else "—",
         "value": float(r["value"] or 0)}
        for r in rows
    ]


@register_data_source("invoicing.revenue_total")
def invoicing_revenue_total(company, period: str = "this_month", **_):
    from modules.invoicing.models import Invoice

    start = _period_start(period)
    agg = Invoice.objects.filter(
        company=company,
        status__in=["posted", "paid"],
        invoice_date__gte=start.date(),
    ).aggregate(total=Sum("total_amount"))
    return {"value": f"${agg['total'] or 0:,.2f}", "detail": period.replace("_", " ")}


@register_data_source("invoicing.invoices_by_status")
def invoicing_invoices_by_status(company, **_):
    from modules.invoicing.models import Invoice

    rows = (
        Invoice.objects.filter(company=company)
        .values("status")
        .annotate(value=Count("id"))
        .order_by("status")
    )
    return [{"group": r["status"] or "—", "value": r["value"]} for r in rows]


# ────────────────────────────────────────────────────────────────────────
# Sales
# ────────────────────────────────────────────────────────────────────────


@register_data_source("sales.open_orders_count")
def sales_open_orders_count(company, **_):
    from modules.sales.models import SalesOrder

    count = SalesOrder.objects.filter(
        company=company, status__in=["confirmed", "in_progress"]
    ).count()
    return {"value": str(count), "detail": "in progress"}


@register_data_source("sales.top_customers")
def sales_top_customers(company, limit: int = 5, **_):
    from modules.sales.models import SalesOrder

    rows = (
        SalesOrder.objects.filter(company=company)
        .values("customer_name")
        .annotate(value=Sum("total_amount"))
        .order_by("-value")[:limit]
    )
    return [
        {"group": r["customer_name"] or "—", "value": float(r["value"] or 0)}
        for r in rows
    ]


@register_data_source("sales.orders_by_status")
def sales_orders_by_status(company, **_):
    from modules.sales.models import SalesOrder

    rows = (
        SalesOrder.objects.filter(company=company)
        .values("status")
        .annotate(value=Count("id"))
        .order_by("status")
    )
    return [{"group": r["status"] or "—", "value": r["value"]} for r in rows]


# ────────────────────────────────────────────────────────────────────────
# Inventory
# ────────────────────────────────────────────────────────────────────────


@register_data_source("inventory.products_count")
def inventory_products_count(company, **_):
    from modules.inventory.models import Product

    count = Product.objects.filter(company=company, is_active=True).count()
    return {"value": str(count), "detail": "active products"}


@register_data_source("inventory.low_stock_items")
def inventory_low_stock(company, limit: int = 10, **_):
    """Products whose on-hand quantity is at or below reorder_point.

    Simplified — production would compute on-hand via StockMove rollup.
    For v1, treat ``reorder_point > 0`` as the alert proxy.
    """
    from modules.inventory.models import Product

    rows = Product.objects.filter(
        company=company, reorder_point__gt=0, is_active=True
    ).values("name", "reorder_point", "unit_of_measure")[:limit]
    return [
        {
            "name": r["name"],
            "reorder_point": float(r["reorder_point"] or 0),
            "unit": r["unit_of_measure"],
        }
        for r in rows
    ]


# ────────────────────────────────────────────────────────────────────────
# Helpdesk
# ────────────────────────────────────────────────────────────────────────


@register_data_source("helpdesk.open_tickets_count")
def helpdesk_open_tickets_count(company, **_):
    from modules.helpdesk.models import Ticket

    count = (
        Ticket.objects.filter(company=company)
        .exclude(status__in=["resolved", "closed"])
        .count()
    )
    return {"value": str(count), "detail": "open tickets"}


@register_data_source("helpdesk.tickets_by_priority")
def helpdesk_tickets_by_priority(company, **_):
    from modules.helpdesk.models import Ticket

    rows = (
        Ticket.objects.filter(company=company)
        .exclude(status__in=["resolved", "closed"])
        .values("priority")
        .annotate(value=Count("id"))
        .order_by("priority")
    )
    return [{"group": r["priority"] or "—", "value": r["value"]} for r in rows]


# ────────────────────────────────────────────────────────────────────────
# Calendar
# ────────────────────────────────────────────────────────────────────────


@register_data_source("calendar.events_today")
def calendar_events_today(company, **_):
    from modules.calendar.models import Event

    start = _period_start("today")
    end = start + timedelta(days=1)
    count = Event.objects.filter(
        company=company, start_datetime__gte=start, start_datetime__lt=end
    ).count()
    return {"value": str(count), "detail": "today"}


@register_data_source("calendar.events_this_week")
def calendar_events_this_week(company, **_):
    from modules.calendar.models import Event

    start = _period_start("last_7_days")
    rows = (
        Event.objects.filter(company=company, start_datetime__gte=start)
        .annotate(day=TruncDay("start_datetime"))
        .values("day")
        .annotate(value=Count("id"))
        .order_by("day")
    )
    return [
        {"group": r["day"].date().isoformat() if r["day"] else "—",
         "value": r["value"]}
        for r in rows
    ]


# ────────────────────────────────────────────────────────────────────────
# HR
# ────────────────────────────────────────────────────────────────────────


@register_data_source("hr.active_employees")
def hr_active_employees(company, **_):
    from modules.hr.models import Employee

    count = Employee.objects.filter(company=company).count()
    return {"value": str(count), "detail": "employees"}


@register_data_source("hr.employees_by_department")
def hr_employees_by_department(company, **_):
    from modules.hr.models import Employee

    rows = (
        Employee.objects.filter(company=company)
        .values("department__name")
        .annotate(value=Count("id"))
        .order_by("-value")
    )
    return [
        {"group": r["department__name"] or "—", "value": r["value"]}
        for r in rows
    ]


# ────────────────────────────────────────────────────────────────────────
# Purchasing
# ────────────────────────────────────────────────────────────────────────


@register_data_source("purchasing.open_pos_count")
def purchasing_open_pos_count(company, **_):
    from modules.purchasing.models import PurchaseOrder

    count = PurchaseOrder.objects.filter(
        company=company, status__in=["draft", "sent", "confirmed"]
    ).count()
    return {"value": str(count), "detail": "open"}


@register_data_source("purchasing.spend_by_vendor")
def purchasing_spend_by_vendor(company, limit: int = 5, **_):
    from modules.purchasing.models import PurchaseOrder

    rows = (
        PurchaseOrder.objects.filter(company=company)
        .values("vendor__name")
        .annotate(value=Sum("total_amount"))
        .order_by("-value")[:limit]
    )
    return [
        {"group": r["vendor__name"] or "—", "value": float(r["value"] or 0)}
        for r in rows
    ]


# ────────────────────────────────────────────────────────────────────────
# Projects
# ────────────────────────────────────────────────────────────────────────


@register_data_source("projects.active_projects_count")
def projects_active_count(company, **_):
    from modules.projects.models import Project

    count = Project.objects.filter(
        company=company, status__in=["planned", "in_progress"]
    ).count()
    return {"value": str(count), "detail": "active"}


@register_data_source("projects.tasks_by_status")
def projects_tasks_by_status(company, **_):
    from modules.projects.models import Task

    rows = (
        Task.objects.filter(company=company)
        .values("status")
        .annotate(value=Count("id"))
        .order_by("status")
    )
    return [{"group": r["status"] or "—", "value": r["value"]} for r in rows]
