from rest_framework import viewsets

from api.v1.aggregation import AggregationMixin
from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.accounting.models import Account, Journal, JournalEntry, JournalEntryLine
from modules.accounting.serializers import (
    AccountSerializer,
    JournalEntryLineSerializer,
    JournalEntrySerializer,
    JournalSerializer,
)


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Account.objects.select_related("parent").order_by("code")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        account_type = self.request.query_params.get("account_type")
        if account_type:
            qs = qs.filter(account_type=account_type)
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs


class JournalViewSet(viewsets.ModelViewSet):
    serializer_class = JournalSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Journal.objects.order_by("name")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        journal_type = self.request.query_params.get("journal_type")
        if journal_type:
            qs = qs.filter(journal_type=journal_type)
        return qs


class JournalEntryViewSet(AggregationMixin, viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = JournalEntry.objects.select_related("journal").order_by(
        "-entry_date", "-created_at"
    )
    pagination_class = None

    aggregatable_fields = frozenset({"status", "journal", "entry_date"})
    aggregatable_measures = frozenset({"id"})

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        journal = self.request.query_params.get("journal")
        if journal:
            qs = qs.filter(journal_id=journal)
        return qs


class JournalEntryLineViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntryLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = JournalEntryLine.objects.select_related("account").order_by("pk")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()
        journal_entry = self.request.query_params.get("journal_entry")
        if journal_entry:
            qs = qs.filter(journal_entry_id=journal_entry)
        return qs
