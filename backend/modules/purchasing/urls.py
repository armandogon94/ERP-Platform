from rest_framework.routers import DefaultRouter

from modules.purchasing.viewsets import (
    POLineViewSet,
    PurchaseOrderViewSet,
    RequestForQuoteViewSet,
    RFQLineViewSet,
    VendorViewSet,
)

router = DefaultRouter()
router.register("vendors", VendorViewSet, basename="vendor")
router.register("purchase-orders", PurchaseOrderViewSet, basename="purchase-order")
router.register("po-lines", POLineViewSet, basename="po-line")
router.register("rfqs", RequestForQuoteViewSet, basename="rfq")
router.register("rfq-lines", RFQLineViewSet, basename="rfq-line")

urlpatterns = router.urls
