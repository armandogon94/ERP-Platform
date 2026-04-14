from rest_framework import serializers

from modules.accounting.models import Account, Journal, JournalEntry, JournalEntryLine


class AccountSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(
        source="parent.name", read_only=True, default=None
    )

    class Meta:
        model = Account
        fields = [
            "id",
            "code",
            "name",
            "account_type",
            "parent",
            "parent_name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "parent_name", "created_at", "updated_at"]


class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = [
            "id",
            "name",
            "code",
            "journal_type",
            "default_account",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class JournalEntryLineSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source="account.name", read_only=True)

    class Meta:
        model = JournalEntryLine
        fields = [
            "id",
            "journal_entry",
            "account",
            "account_name",
            "label",
            "debit",
            "credit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "account_name", "created_at", "updated_at"]


class JournalEntrySerializer(serializers.ModelSerializer):
    journal_name = serializers.CharField(source="journal.name", read_only=True)

    class Meta:
        model = JournalEntry
        fields = [
            "id",
            "journal",
            "journal_name",
            "reference",
            "entry_date",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "journal_name", "created_at", "updated_at"]
