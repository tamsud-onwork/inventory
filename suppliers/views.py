
import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Supplier, SupplierProduct
from .serializers import SupplierSerializer, SupplierProductSerializer
from inventory_api.permissions import RolePermission
from inventory_api.exceptions import InventoryError

logger = logging.getLogger('inventory')

# Create your views here.

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('id')
    serializer_class = SupplierSerializer
    permission_classes = [RolePermission]
    def get_permissions(self):
        return [RolePermission(allowed_roles=['admin', 'manager'])]

    def create(self, request, *args, **kwargs):
        logger.info('Supplier create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)

class SupplierProductViewSet(viewsets.ModelViewSet):
    queryset = SupplierProduct.objects.all().order_by('id')
    serializer_class = SupplierProductSerializer
    permission_classes = [RolePermission]
    def get_permissions(self):
        return [RolePermission(allowed_roles=['admin', 'manager'])]

    def create(self, request, *args, **kwargs):
        logger.info('SupplierProduct create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)
