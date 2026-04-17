"""Model tests for the Reports module (Slice 16)."""

import pytest

from core.factories import CompanyFactory
from modules.reports.factories import (
    PivotDefinitionFactory,
    ReportTemplateFactory,
    ScheduledExportFactory,
)
from modules.reports.models import PivotDefinition, ReportTemplate, ScheduledExport


@pytest.mark.django_db
class TestReportTemplate:
    def test_create(self):
        r = ReportTemplateFactory(name="Revenue by Month")
        assert r.pk is not None
        assert r.model_name == "invoicing.Invoice"

    def test_company_isolation(self):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        ReportTemplateFactory(company=a)
        ReportTemplateFactory(company=b)
        assert ReportTemplate.objects.filter(company=a).count() == 1


@pytest.mark.django_db
class TestPivotDefinition:
    def test_create(self):
        p = PivotDefinitionFactory(measure="total_amount", aggregator="sum")
        assert p.pk is not None
        assert p.aggregator == "sum"

    def test_str(self):
        p = PivotDefinitionFactory(name="Sales by Status")
        assert str(p) == "Sales by Status"


@pytest.mark.django_db
class TestScheduledExport:
    def test_create(self):
        s = ScheduledExportFactory()
        assert s.pk is not None
        assert s.active is True

    def test_format_default_pdf(self):
        s = ScheduledExportFactory()
        assert s.format == ScheduledExport.Format.PDF
