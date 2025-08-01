import logging
from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Stock, StockMovement, StockAdjustment
from .serializers import StockSerializer, StockMovementSerializer, StockAdjustmentSerializer
from inventory_api.permissions import RolePermission
from inventory_api.exceptions import (
    InventoryError, StockNotAvailableError, PermissionDeniedError,
    ValidationError, NotFoundError, BusinessRuleError
)

logger = logging.getLogger('inventory')

# Create your views here.

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all().order_by('id')
    serializer_class = StockSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [RolePermission(['admin', 'manager'])]
        return [RolePermission(['admin', 'manager', 'employee'])]

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all().order_by('id')
    serializer_class = StockMovementSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [RolePermission(['admin', 'manager'])]
        return [RolePermission(['admin', 'manager', 'employee'])]

    def create(self, request, *args, **kwargs):
        logger.info('Stock movement create requested by user: %s', request.user)
        try:
            return super().create(request, *args, **kwargs)
        except StockNotAvailableError as e:
            logger.warning('Stock not available for movement: %s', e)
            raise
        except ValidationError as e:
            logger.error('Validation error: %s', e)
            raise
        except BusinessRuleError as e:
            logger.error('Business rule violation: %s', e)
            raise
        except Exception as e:
            logger.error('Stock movement creation failed: %s', e)
            raise InventoryError('Failed to create stock movement')

class StockAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = StockAdjustment.objects.all().order_by('id')
    serializer_class = StockAdjustmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [RolePermission(['admin', 'manager'])]
        return [RolePermission(['admin', 'manager', 'employee'])]

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            role = user.employee.role
        except Exception:
            logger.error('Employee object not found for user: %s', user)
            raise PermissionDeniedError('Employee object not found')
        if role not in ['admin', 'manager']:
            logger.warning('Permission denied for role: %s', role)
            raise PermissionDeniedError('Only manager or admin can approve stock adjustments.')
        return super().create(request, *args, **kwargs)
