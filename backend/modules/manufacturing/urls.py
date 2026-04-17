from django.urls import include, path
from rest_framework.routers import DefaultRouter

from modules.manufacturing.viewsets import (
    BillOfMaterialsViewSet,
    BOMLineViewSet,
    ProductionCostViewSet,
    WorkOrderViewSet,
)

router = DefaultRouter()
router.register("boms", BillOfMaterialsViewSet, basename="bom")
router.register("bom-lines", BOMLineViewSet, basename="bom-line")
router.register("work-orders", WorkOrderViewSet, basename="work-order")
router.register("costs", ProductionCostViewSet, basename="production-cost")

urlpatterns = [path("", include(router.urls))]
