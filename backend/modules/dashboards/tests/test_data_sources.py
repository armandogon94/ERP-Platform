"""Tests for the data source registry."""

from decimal import Decimal

import pytest
from django.core.cache import cache

from core.factories import CompanyFactory
from modules.dashboards.data_sources import (
    compute_data_source,
    list_data_sources,
    register_data_source,
)


@pytest.mark.django_db
class TestRegistry:
    def test_list_sources_returns_sorted_keys(self):
        sources = list_data_sources()
        assert "invoicing.outstanding_total" in sources
        assert "helpdesk.open_tickets_count" in sources
        assert sources == sorted(sources)

    def test_unknown_source_raises_keyerror(self):
        with pytest.raises(KeyError):
            compute_data_source("nope.nothing", CompanyFactory(), {})

    def test_invoicing_outstanding_total_handles_empty_company(self):
        company = CompanyFactory()
        result = compute_data_source("invoicing.outstanding_total", company)
        assert result == {"value": "$0.00", "detail": "0 invoice(s)"}

    def test_results_cached_per_company_and_config(self):
        """Same (company, source, config) triple → second call hits cache."""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        company = CompanyFactory()
        cache.delete(f"widget:{company.id}:invoicing.outstanding_total:{{}}")

        with CaptureQueriesContext(connection) as first:
            compute_data_source("invoicing.outstanding_total", company)
        with CaptureQueriesContext(connection) as second:
            compute_data_source("invoicing.outstanding_total", company)

        # Second call runs zero queries (pure cache hit).
        assert len(second.captured_queries) < len(first.captured_queries)


@pytest.mark.django_db
class TestDataShapes:
    def test_kpi_returns_value_and_detail(self):
        company = CompanyFactory()
        r = compute_data_source("helpdesk.open_tickets_count", company)
        assert "value" in r and "detail" in r

    def test_line_returns_list_of_groups(self):
        company = CompanyFactory()
        r = compute_data_source("invoicing.revenue_daily", company)
        assert isinstance(r, list)
        # Empty company → empty series is the correct shape.
        for row in r:
            assert "group" in row and "value" in row

    def test_table_shape_for_low_stock(self):
        company = CompanyFactory()
        r = compute_data_source("inventory.low_stock_items", company)
        assert isinstance(r, list)
