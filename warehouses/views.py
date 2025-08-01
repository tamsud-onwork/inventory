
import logging
from rest_framework import viewsets
from .models import Warehouse, Location
from .serializers import WarehouseSerializer, LocationSerializer
from inventory_api.permissions import RolePermission
from inventory_api.exceptions import InventoryError

logger = logging.getLogger('inventory')

# Create your views here.

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all().order_by('id')
    serializer_class = WarehouseSerializer
    permission_classes = [RolePermission]
    def get_permissions(self):
        return [RolePermission(allowed_roles=['admin', 'manager'])]

    def create(self, request, *args, **kwargs):
        logger.info('Warehouse create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('id')
    serializer_class = LocationSerializer
    permission_classes = [RolePermission]
    def get_permissions(self):
        return [RolePermission(allowed_roles=['admin', 'manager'])]

    def create(self, request, *args, **kwargs):
        logger.info('Location create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)
