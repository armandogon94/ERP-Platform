"""Model tests for the Helpdesk module (Slice 15)."""

import pytest

from core.factories import CompanyFactory, PartnerFactory, UserFactory
from modules.helpdesk.factories import (
    KnowledgeArticleFactory,
    SLAConfigFactory,
    TicketCategoryFactory,
    TicketFactory,
)
from modules.helpdesk.models import (
    KnowledgeArticle,
    SLAConfig,
    Ticket,
    TicketCategory,
)


@pytest.mark.django_db
class TestTicketCategory:
    def test_create(self):
        cat = TicketCategoryFactory()
        assert cat.pk is not None
        assert cat.sla_hours >= 0

    def test_str(self):
        cat = TicketCategoryFactory(name="Billing")
        assert str(cat) == "Billing"

    def test_company_isolation(self):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        TicketCategoryFactory(company=a)
        TicketCategoryFactory(company=b)
        assert TicketCategory.objects.filter(company=a).count() == 1


@pytest.mark.django_db
class TestSLAConfig:
    def test_create(self):
        sla = SLAConfigFactory()
        assert sla.pk is not None
        assert sla.priority == SLAConfig.Priority.NORMAL
        assert sla.response_hours > 0


@pytest.mark.django_db
class TestTicket:
    def test_create(self):
        t = TicketFactory()
        assert t.pk is not None
        assert t.status == Ticket.Status.NEW

    def test_auto_ticket_number(self):
        t = TicketFactory(ticket_number="")
        assert t.ticket_number.startswith("TKT/")

    def test_preset_number_preserved(self):
        t = TicketFactory(ticket_number="MANUAL-1")
        assert t.ticket_number == "MANUAL-1"

    def test_reporter_partner_optional(self):
        t = TicketFactory(reporter_partner=None, reporter_user=None)
        assert t.reporter_partner is None
        assert t.reporter_user is None

    def test_reporter_partner_assignment(self):
        company = CompanyFactory()
        partner = PartnerFactory(company=company, is_customer=True)
        t = TicketFactory(company=company, reporter_partner=partner)
        assert t.reporter_partner_id == partner.id

    def test_assignee_user_fk(self):
        company = CompanyFactory()
        user = UserFactory(company=company)
        t = TicketFactory(company=company, assignee=user)
        assert t.assignee_id == user.id

    def test_sla_breached_default_false(self):
        t = TicketFactory()
        assert t.sla_breached is False


@pytest.mark.django_db
class TestKnowledgeArticle:
    def test_create(self):
        a = KnowledgeArticleFactory()
        assert a.pk is not None
        assert a.published is False

    def test_slug_unique_per_company(self):
        company = CompanyFactory()
        KnowledgeArticleFactory(
            company=company, slug="how-to-reset", title="How to reset"
        )
        # Different company slug is allowed
        other = CompanyFactory(slug="other")
        KnowledgeArticleFactory(
            company=other, slug="how-to-reset", title="How to reset"
        )
        assert (
            KnowledgeArticle.all_objects.filter(slug="how-to-reset").count() == 2
        )
