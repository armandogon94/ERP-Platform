from django.urls import include, path
from rest_framework.routers import DefaultRouter

from modules.pos.viewsets import (
    CashMovementViewSet,
    POSOrderLineViewSet,
    POSOrderViewSet,
    POSSessionViewSet,
)

router = DefaultRouter()
router.register("sessions", POSSessionViewSet, basename="pos-session")
router.register("orders", POSOrderViewSet, basename="pos-order")
router.register("order-lines", POSOrderLineViewSet, basename="pos-order-line")
router.register("cash-movements", CashMovementViewSet, basename="pos-cash-movement")

urlpatterns = [path("", include(router.urls))]
