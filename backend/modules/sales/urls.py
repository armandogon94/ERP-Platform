from rest_framework.routers import DefaultRouter

from modules.sales.viewsets import (
    SalesOrderLineViewSet,
    SalesOrderViewSet,
    SalesQuotationViewSet,
)

router = DefaultRouter()
router.register("quotations", SalesQuotationViewSet, basename="quotation")
router.register("orders", SalesOrderViewSet, basename="sales-order")
router.register("order-lines", SalesOrderLineViewSet, basename="sales-order-line")

urlpatterns = router.urls
