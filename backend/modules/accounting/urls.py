from rest_framework.routers import DefaultRouter

from modules.accounting.viewsets import (
    AccountViewSet,
    JournalEntryLineViewSet,
    JournalEntryViewSet,
    JournalViewSet,
)

router = DefaultRouter()
router.register("accounts", AccountViewSet, basename="account")
router.register("journals", JournalViewSet, basename="journal")
router.register("entries", JournalEntryViewSet, basename="journal-entry")
router.register("entry-lines", JournalEntryLineViewSet, basename="journal-entry-line")

urlpatterns = router.urls
