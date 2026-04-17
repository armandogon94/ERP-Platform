import factory

from core.factories import CompanyFactory
from modules.reports.models import PivotDefinition, ReportTemplate, ScheduledExport


class ReportTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReportTemplate
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Report {n}")
    model_name = "invoicing.Invoice"
    default_filters = factory.LazyFunction(dict)
    default_group_by = factory.LazyFunction(list)
    default_measures = factory.LazyFunction(list)


class PivotDefinitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PivotDefinition
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Pivot {n}")
    model_name = "invoicing.Invoice"
    rows = factory.LazyFunction(list)
    cols = factory.LazyFunction(list)
    measure = "total_amount"
    aggregator = "sum"


class ScheduledExportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScheduledExport
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    report = factory.SubFactory(
        ReportTemplateFactory, company=factory.SelfAttribute("..company")
    )
    cron = "0 8 * * 1"
    format = ScheduledExport.Format.PDF
    recipients = factory.LazyFunction(list)
    active = True
