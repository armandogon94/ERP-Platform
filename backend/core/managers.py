from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet that filters out soft-deleted records by default."""

    def delete(self):
        """Soft delete all records in the queryset."""
        from django.utils import timezone

        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        """Actually delete records from the database."""
        return super().delete()

    def with_deleted(self):
        """Return a new queryset that includes soft-deleted records."""
        return self.model._default_manager.all_with_deleted()


class SoftDeleteManager(models.Manager):
    """Default manager that excludes soft-deleted records."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True
        )

    def all_with_deleted(self):
        """Return all records including soft-deleted ones."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """Return only soft-deleted records."""
        return SoftDeleteQuerySet(self.model, using=self._db).exclude(
            deleted_at__isnull=True
        )
