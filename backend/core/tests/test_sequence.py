import pytest
from django.db import connection

from core.factories import CompanyFactory
from core.sequence import get_next_sequence


@pytest.mark.django_db
class TestSequenceGeneration:
    def test_first_sequence_starts_at_one(self):
        company = CompanyFactory()
        result = get_next_sequence(company, "INV")
        assert result.startswith("INV/")
        assert result.endswith("/00001")

    def test_sequential_numbers_increment(self):
        company = CompanyFactory()
        first = get_next_sequence(company, "PO")
        second = get_next_sequence(company, "PO")
        third = get_next_sequence(company, "PO")

        assert first.endswith("/00001")
        assert second.endswith("/00002")
        assert third.endswith("/00003")

    def test_different_prefixes_independent(self):
        company = CompanyFactory()
        inv = get_next_sequence(company, "INV")
        po = get_next_sequence(company, "PO")

        assert inv.endswith("/00001")
        assert po.endswith("/00001")

    def test_different_companies_independent(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()

        seq_a = get_next_sequence(company_a, "INV")
        seq_b = get_next_sequence(company_b, "INV")

        assert seq_a.endswith("/00001")
        assert seq_b.endswith("/00001")

    def test_format_includes_year(self):
        from django.utils import timezone

        company = CompanyFactory()
        result = get_next_sequence(company, "SO")
        year = timezone.now().year
        assert f"SO/{year}/00001" == result

    def test_padding_respects_sequence_config(self):
        from core.models import Sequence

        company = CompanyFactory()
        Sequence.objects.create(
            company=company,
            prefix="CUST",
            next_number=1,
            step=1,
            padding=8,
            use_date_range=False,
        )
        result = get_next_sequence(company, "CUST")
        assert result == "CUST/00000001"

    def test_no_date_range_format(self):
        from core.models import Sequence

        company = CompanyFactory()
        Sequence.objects.create(
            company=company,
            prefix="REF",
            next_number=42,
            step=1,
            padding=5,
            use_date_range=False,
        )
        result = get_next_sequence(company, "REF")
        assert result == "REF/00042"

    def test_custom_step_size(self):
        from core.models import Sequence

        company = CompanyFactory()
        Sequence.objects.create(
            company=company,
            prefix="LOT",
            next_number=100,
            step=10,
            padding=5,
            use_date_range=False,
        )
        first = get_next_sequence(company, "LOT")
        second = get_next_sequence(company, "LOT")

        assert first == "LOT/00100"
        assert second == "LOT/00110"
