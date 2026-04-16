"""Tests for the Partner model (Slice 10.6, D21).

Partner is a unified customer+vendor entity (Odoo pattern). Every Company
has its own Partners; cross-company access is forbidden by the tenant
filter backend.
"""

import pytest
from django.db import IntegrityError

from core.factories import CompanyFactory
from core.models import Partner


@pytest.mark.django_db
class TestPartnerModel:
    def test_create_minimal_partner(self):
        company = CompanyFactory()
        partner = Partner.objects.create(
            company=company,
            name="Acme Corporation",
            is_customer=True,
        )
        assert partner.pk is not None
        assert partner.name == "Acme Corporation"
        assert partner.is_customer is True
        assert partner.is_vendor is False
        assert partner.email == ""  # default blank

    def test_str_returns_name(self):
        company = CompanyFactory()
        partner = Partner.objects.create(
            company=company,
            name="Globex Inc",
            is_vendor=True,
        )
        assert str(partner) == "Globex Inc"

    def test_partner_can_be_both_customer_and_vendor(self):
        company = CompanyFactory()
        partner = Partner.objects.create(
            company=company,
            name="Dual Role Partner",
            is_customer=True,
            is_vendor=True,
        )
        assert partner.is_customer is True
        assert partner.is_vendor is True

    def test_company_isolation(self):
        company_a = CompanyFactory(slug="co-a")
        company_b = CompanyFactory(slug="co-b")
        Partner.objects.create(company=company_a, name="A-Only Partner")
        Partner.objects.create(company=company_b, name="B-Only Partner")
        a_names = list(
            Partner.objects.filter(company=company_a).values_list("name", flat=True)
        )
        b_names = list(
            Partner.objects.filter(company=company_b).values_list("name", flat=True)
        )
        assert "A-Only Partner" in a_names
        assert "A-Only Partner" not in b_names
        assert "B-Only Partner" in b_names
        assert "B-Only Partner" not in a_names

    def test_same_name_allowed_in_different_companies(self):
        company_a = CompanyFactory(slug="co-a")
        company_b = CompanyFactory(slug="co-b")
        Partner.objects.create(company=company_a, name="Acme")
        # Should NOT raise — uniqueness is per-company.
        Partner.objects.create(company=company_b, name="Acme")

    def test_duplicate_name_same_company_raises(self):
        company = CompanyFactory()
        Partner.objects.create(company=company, name="Acme", tax_id="US-111")
        with pytest.raises(IntegrityError):
            Partner.objects.create(company=company, name="Acme", tax_id="US-111")

    def test_fields_have_sensible_defaults(self):
        company = CompanyFactory()
        partner = Partner.objects.create(company=company, name="Default Partner")
        assert partner.is_customer is False
        assert partner.is_vendor is False
        assert partner.email == ""
        assert partner.phone == ""
        assert partner.tax_id == ""
        assert partner.payment_terms_days == 0
        assert float(partner.credit_limit) == 0.0
        assert partner.industry_tags == []
        assert partner.address_json == {}

    def test_soft_delete_excludes_from_default_manager(self):
        company = CompanyFactory()
        partner = Partner.objects.create(company=company, name="Soft Delete Target")
        partner.soft_delete()
        assert Partner.objects.filter(pk=partner.pk).count() == 0
        assert Partner.all_objects.filter(pk=partner.pk).count() == 1
