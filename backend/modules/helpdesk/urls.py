from django.urls import include, path
from rest_framework.routers import DefaultRouter

from modules.helpdesk.viewsets import (
    KnowledgeArticleViewSet,
    SLAConfigViewSet,
    TicketCategoryViewSet,
    TicketViewSet,
)

router = DefaultRouter()
router.register("categories", TicketCategoryViewSet, basename="ticket-category")
router.register("sla-configs", SLAConfigViewSet, basename="sla-config")
router.register("tickets", TicketViewSet, basename="ticket")
router.register("articles", KnowledgeArticleViewSet, basename="knowledge-article")

urlpatterns = [path("", include(router.urls))]
