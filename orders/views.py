
import logging
from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem
from .serializers import PurchaseOrderSerializer, PurchaseOrderItemSerializer, SalesOrderSerializer, SalesOrderItemSerializer
from inventory_api.permissions import RolePermission
from inventory_api.exceptions import InventoryError, StockNotAvailableError

logger = logging.getLogger('inventory')

# Create your views here.

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('id')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [type('CustomRolePermission', (RolePermission,), {'__init__': lambda self: RolePermission.__init__(self, ['admin', 'manager'])})]

    from rest_framework.decorators import action
    from rest_framework.response import Response

    @action(detail=True, methods=['post'], url_path='receive')
    def receive(self, request, pk=None):
        po = self.get_object()
        if po.status == 'received':
            return self.Response({'detail': 'Already received'}, status=400)
        from inventory.models import Stock
        from .models import PurchaseOrderItem
        items = PurchaseOrderItem.objects.filter(purchase_order=po)
        for item in items:
            # Find a location for the product's warehouse, or create one if needed
            from warehouses.models import Location, Warehouse
            warehouse = None
            if hasattr(item.product, 'category') and hasattr(item.product.category, 'name'):
                warehouse = Warehouse.objects.first()
            else:
                warehouse = Warehouse.objects.first()
            location = Location.objects.filter(warehouse=warehouse).first()
            if not location:
                location = Location.objects.create(warehouse=warehouse, name='Default', type='Bin')
            stock, created = Stock.objects.get_or_create(product=item.product, location=location)
            stock.quantity += item.quantity
            stock.save()
        po.status = 'received'
        po.save()
        return self.Response({'detail': 'Stock incremented and PO marked as received'})

class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderItem.objects.all().order_by('id')
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [type('CustomRolePermission', (RolePermission,), {'__init__': lambda self: RolePermission.__init__(self, ['admin', 'manager'])})]

class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all().order_by('id')
    serializer_class = SalesOrderSerializer
    permission_classes = [type('CustomRolePermission', (RolePermission,), {'__init__': lambda self: RolePermission.__init__(self, ['admin', 'manager', 'employee'])})]

    def create(self, request, *args, **kwargs):
        items = request.data.get('items', [])
        from inventory.models import Stock
        errors = []
        stock_to_update = []
        logger.info('Sales order create requested by user: %s', request.user)
        try:
            for item in items:
                product_id = item.get('product')
                quantity = int(item.get('quantity', 0))
                stock_qs = Stock.objects.filter(product_id=product_id)
                total_stock = sum([s.quantity for s in stock_qs])
                if quantity > total_stock:
                    errors.append(f"Stock not available for product {product_id}. Requested: {quantity}, Available: {total_stock}")
                else:
                    # Prepare deduction
                    stock_to_update.append((stock_qs, quantity))
        except StockNotAvailableError as e:
            logger.warning('Stock not available for sales order: %s', e)
            raise
        if errors:
            from rest_framework.response import Response
            return Response({'detail': 'Stock not available', 'errors': errors}, status=400)
        # Deduct stock (FIFO)
        for stock_qs, quantity in stock_to_update:
            for stock in stock_qs.order_by('id'):
                if quantity <= 0:
                    break
                deduct = min(stock.quantity, quantity)
                stock.quantity -= deduct
                stock.save()
                quantity -= deduct
        return super().create(request, *args, **kwargs)

class SalesOrderItemViewSet(viewsets.ModelViewSet):
    queryset = SalesOrderItem.objects.all().order_by('id')
    serializer_class = SalesOrderItemSerializer
    permission_classes = [type('CustomRolePermission', (RolePermission,), {'__init__': lambda self: RolePermission.__init__(self, ['admin', 'manager', 'employee'])})]

    def create(self, request, *args, **kwargs):
        logger.info('Sales order item create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)

class SalesOrderItemViewSet(viewsets.ModelViewSet):
    queryset = SalesOrderItem.objects.all()
    serializer_class = SalesOrderItemSerializer
    permission_classes = [type('CustomRolePermission', (RolePermission,), {'__init__': lambda self: RolePermission.__init__(self, ['admin', 'manager', 'employee'])})]
