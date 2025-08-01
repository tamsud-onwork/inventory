from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, CustomerViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'customers', CustomerViewSet)

urlpatterns = router.urls
