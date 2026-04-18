"""Reusable DRF mixins for module ViewSets.

REVIEW I-12 — ``FilterParamsMixin`` kills ~200 lines of hand-rolled
``get_queryset`` boilerplate across fleet, projects, manufacturing,
helpdesk, pos, inventory, etc. Before this mixin, every ViewSet
re-implemented the same query-params-to-filter pattern and occasionally
forgot the ``_id`` suffix on FK lookups, producing subtle bugs.
"""

from __future__ import annotations


class FilterParamsMixin:
    """Declaratively map query-string params to queryset filters.

    Subclass with ``filter_params`` to get a ``get_queryset`` that
    ANDs together every matching param into a single ``.filter()`` call.

    Syntax::

        filter_params = {
            # query param name → model field lookup
            "status": "status",
            "driver":  "driver_id",
            "vehicle": "vehicle_id",
            # bool params
            "active":  "active__bool",
        }

    Values::

        "<field>"              # direct equality match
        "<field>__bool"        # string-to-bool coercion (``"true"``/``"false"``)

    Works in composition with an existing custom ``get_queryset`` — just
    call ``super().get_queryset()`` and the mixin handles the params. If
    you define ``get_queryset`` yourself AFTER the mixin, the mixin's
    logic runs first via the MRO chain.
    """

    filter_params: dict[str, str] = {}

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        for param_name, field_spec in self.filter_params.items():
            raw = params.get(param_name)
            if raw is None or raw == "":
                continue
            if field_spec.endswith("__bool"):
                field = field_spec[: -len("__bool")]
                qs = qs.filter(**{field: raw.lower() == "true"})
            else:
                qs = qs.filter(**{field_spec: raw})
        return qs
