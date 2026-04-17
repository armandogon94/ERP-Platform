"""Sequence auto-generation for JournalEntry (Slice 10.7)."""

import pytest

from core.factories import CompanyFactory
from modules.accounting.factories import JournalEntryFactory, JournalFactory


@pytest.mark.django_db
class TestJournalEntrySequenceAutogen:
    def test_blank_reference_is_auto_generated(self):
        company = CompanyFactory()
        journal = JournalFactory(company=company)
        je = JournalEntryFactory(company=company, journal=journal, reference="")
        assert je.reference.startswith("JE/")
        assert je.reference.endswith("/00001")

    def test_preset_reference_is_preserved(self):
        company = CompanyFactory()
        journal = JournalFactory(company=company)
        je = JournalEntryFactory(
            company=company, journal=journal, reference="MANUAL-JE-1"
        )
        assert je.reference == "MANUAL-JE-1"

    def test_second_entry_increments(self):
        company = CompanyFactory()
        journal = JournalFactory(company=company)
        first = JournalEntryFactory(company=company, journal=journal, reference="")
        second = JournalEntryFactory(company=company, journal=journal, reference="")
        assert first.reference.endswith("/00001")
        assert second.reference.endswith("/00002")
