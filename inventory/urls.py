from rest_framework.routers import DefaultRouter
from .views import StockViewSet, StockMovementViewSet, StockAdjustmentViewSet

router = DefaultRouter()
router.register(r'stock', StockViewSet, basename='stock')
router.register(r'stock-movements', StockMovementViewSet, basename='stockmovement')
router.register(r'stock-adjustments', StockAdjustmentViewSet, basename='stockadjustment')

urlpatterns = router.urls
