import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Category, Product, ProductVariant
from .serializers import CategorySerializer, ProductSerializer, ProductVariantSerializer
from inventory_api.permissions import RolePermission
from inventory_api.exceptions import InventoryError, PermissionDeniedError

logger = logging.getLogger('inventory')

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info('Category create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer

    permission_classes = [RolePermission]
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [RolePermission(allowed_roles=['admin', 'manager'])]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        logger.info('Product create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all().order_by('id')
    serializer_class = ProductVariantSerializer

    permission_classes = [RolePermission]
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [RolePermission(allowed_roles=['admin', 'manager'])]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        logger.info('ProductVariant create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)
