"""Pagination classes for the v1 API.

``DefaultCursorPagination`` is the cursor-style class for endpoints that want
real pagination (``?cursor=...``).

``SafeArrayPagination`` is the default — it returns a plain JSON array (no
envelope) but *caps* the result at ``max_page_size`` rows and emits an
``X-Has-More`` / ``X-Result-Count`` header. This is REVIEW C-3's safety net:
previously every ViewSet set ``pagination_class = None``, so a company with
10k invoices would get all 10k in one response. The array shape is preserved
so no frontend changes are required.

Endpoints that want real cursor paging (e.g. an infinite-scroll list) should
override with ``pagination_class = DefaultCursorPagination`` explicitly.
"""

from rest_framework.pagination import BasePagination, CursorPagination
from rest_framework.response import Response


class DefaultCursorPagination(CursorPagination):
    ordering = "-created_at"


class SafeArrayPagination(BasePagination):
    """Return a plain array, capped at ``max_page_size`` rows.

    Response headers:

    * ``X-Result-Count`` — number of rows returned (always ≤ max_page_size)
    * ``X-Has-More: true`` — present only when the underlying queryset had
      more rows than were returned (client should narrow its filter)
    """

    max_page_size = 500

    def paginate_queryset(self, queryset, request, view=None):
        # Only cap if the endpoint is actually a list. DRF calls this for the
        # list action; retrieve/create/etc. don't hit pagination.
        self._truncated = False
        self._count = None
        # Slice one extra to detect overflow cheaply.
        items = list(queryset[: self.max_page_size + 1])
        if len(items) > self.max_page_size:
            self._truncated = True
            items = items[: self.max_page_size]
        self._count = len(items)
        return items

    def get_paginated_response(self, data):
        headers = {"X-Result-Count": str(self._count or 0)}
        if self._truncated:
            headers["X-Has-More"] = "true"
        return Response(data, headers=headers)

    def get_paginated_response_schema(self, schema):
        return schema  # arrays, not envelopes
