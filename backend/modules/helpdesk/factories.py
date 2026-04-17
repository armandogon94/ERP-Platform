import factory

from core.factories import CompanyFactory
from modules.helpdesk.models import (
    KnowledgeArticle,
    SLAConfig,
    Ticket,
    TicketCategory,
)


class TicketCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TicketCategory
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Category {n}")
    sla_hours = 24
    industry_tag = ""


class SLAConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SLAConfig
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    category = factory.SubFactory(
        TicketCategoryFactory, company=factory.SelfAttribute("..company")
    )
    priority = SLAConfig.Priority.NORMAL
    response_hours = 4
    resolution_hours = 24


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    title = factory.Sequence(lambda n: f"Ticket {n}")
    description = ""
    category = None
    reporter_partner = None
    reporter_user = None
    assignee = None
    priority = Ticket.Priority.NORMAL
    status = Ticket.Status.NEW


class KnowledgeArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = KnowledgeArticle
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    title = factory.Sequence(lambda n: f"Article {n}")
    slug = factory.Sequence(lambda n: f"article-{n}")
    body = ""
    category = None
    published = False
    tags = factory.LazyFunction(list)
