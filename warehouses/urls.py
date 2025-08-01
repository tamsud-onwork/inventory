from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, LocationViewSet

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet)
router.register(r'locations', LocationViewSet)

urlpatterns = router.urls
