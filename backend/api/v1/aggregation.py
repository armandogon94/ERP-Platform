"""Reusable `/aggregate/` endpoint mixin (Slice 16, D23).

A ViewSet that inherits `AggregationMixin` and declares a whitelist of
`aggregatable_fields` + `aggregatable_measures` gains a
`GET /{model}/aggregate/?group_by=<field>&measure=<field>&op=<sum|count|avg>
&filter=<field>__<lookup>=<value>` endpoint that returns
`[{group: <value>, value: <number>}]`.

Security notes (D23):
- Both `group_by` and `measure` are rejected unless they appear in their
  respective whitelist. This prevents SQL injection via ORM `.values()`
  and prevents exfiltration of internal fields (e.g. `deleted_at`).
- Only `sum`, `count`, `avg`, `min`, `max` are allowed for `op`.
- The queryset comes from `get_queryset()` (which already applies
  CompanyScopedFilterBackend), so multi-tenancy is preserved.
- Filters are limited to fields that appear in `aggregatable_fields` and
  a fixed list of safe lookups.
"""

from decimal import Decimal

from django.db.models import Avg, Count, Max, Min, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

AGGREGATORS = {
    "sum": Sum,
    "count": Count,
    "avg": Avg,
    "min": Min,
    "max": Max,
}

SAFE_LOOKUPS = frozenset(
    [
        "",  # exact (no suffix)
        "exact",
        "iexact",
        "contains",
        "icontains",
        "gt",
        "gte",
        "lt",
        "lte",
        "in",
        "isnull",
        "startswith",
        "istartswith",
    ]
)


class AggregationMixin:
    """Adds `@action GET /aggregate/` to a ModelViewSet.

    Subclasses must declare at minimum:
        aggregatable_fields  = frozenset({"status", "customer_id", ...})
        aggregatable_measures = frozenset({"total_amount", "quantity", ...})
    """

    aggregatable_fields: "frozenset[str]" = frozenset()
    aggregatable_measures: "frozenset[str]" = frozenset()

    @action(detail=False, methods=["get"])
    def aggregate(self, request):
        group_by = request.query_params.get("group_by")
        measure = request.query_params.get("measure", "id")
        op = request.query_params.get("op", "count").lower()

        if not group_by:
            return Response({"detail": "group_by is required"}, status=400)
        if group_by not in self.aggregatable_fields:
            return Response(
                {"detail": f"group_by '{group_by}' is not aggregatable"},
                status=400,
            )
        if op == "count":
            # `count` is always safe; measure defaults to primary key.
            measure_field = measure if measure == "id" else measure
            if measure_field != "id" and measure_field not in self.aggregatable_measures:
                return Response(
                    {"detail": f"measure '{measure_field}' is not aggregatable"},
                    status=400,
                )
        else:
            if measure not in self.aggregatable_measures:
                return Response(
                    {"detail": f"measure '{measure}' is not aggregatable"},
                    status=400,
                )

        aggregator = AGGREGATORS.get(op)
        if aggregator is None:
            return Response(
                {"detail": f"op '{op}' not in {sorted(AGGREGATORS)}"},
                status=400,
            )

        qs = self.filter_queryset(self.get_queryset())

        # Apply safe filters from ?filter=<field>__<lookup>=<value>
        for raw_key, raw_value in request.query_params.lists():
            if raw_key in {"group_by", "measure", "op"}:
                continue
            field, _, lookup = raw_key.partition("__")
            if field not in self.aggregatable_fields:
                continue
            if lookup and lookup not in SAFE_LOOKUPS:
                continue
            value = raw_value[0] if len(raw_value) == 1 else raw_value
            qs = qs.filter(**{raw_key: value})

        rows = qs.values(group_by).annotate(value=aggregator(measure)).order_by(group_by)
        return Response(
            [
                {
                    "group": r[group_by],
                    "value": (
                        float(r["value"])
                        if isinstance(r["value"], Decimal)
                        else r["value"]
                    ),
                }
                for r in rows
            ]
        )
