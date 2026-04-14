from rest_framework.routers import DefaultRouter

from modules.inventory.viewsets import (
    ProductCategoryViewSet,
    ProductViewSet,
    ReorderRuleViewSet,
    StockLocationViewSet,
    StockLotViewSet,
    StockMoveViewSet,
)

router = DefaultRouter()
router.register("categories", ProductCategoryViewSet, basename="inventory-category")
router.register("products", ProductViewSet, basename="inventory-product")
router.register("locations", StockLocationViewSet, basename="inventory-location")
router.register("lots", StockLotViewSet, basename="inventory-lot")
router.register("moves", StockMoveViewSet, basename="inventory-move")
router.register("reorder-rules", ReorderRuleViewSet, basename="inventory-reorder-rule")

urlpatterns = router.urls
