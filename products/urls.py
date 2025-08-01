from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductVariantViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-variants', ProductVariantViewSet)

urlpatterns = router.urls
