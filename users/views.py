from django.shortcuts import render
import logging
from inventory_api.exceptions import InventoryError, PermissionDeniedError, ValidationError, NotFoundError, BusinessRuleError
from inventory_api.exceptions import PermissionDeniedError, InventoryError
from rest_framework import viewsets, permissions
from .models import Employee, Customer, User
from .serializers import EmployeeSerializer, CustomerSerializer, UserSerializer
from inventory_api.permissions import RolePermission

logger = logging.getLogger('inventory')

# Example view using custom logger and exception

def example_view(request):
    logger.info('Example view accessed by user: %s', request.user)
    if not request.user.is_authenticated:
        logger.warning('Unauthenticated access attempt')
        raise PermissionDeniedError('You must be logged in to access this view.')
    # ...existing code...
    return render(request, 'users/example.html')

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    permission_classes = [RolePermission]
    def get_permissions(self):
        return [RolePermission(allowed_roles=['admin'])]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [RolePermission]
    def get_permissions(self):
        return [RolePermission(allowed_roles=['admin'])]

    def create(self, request, *args, **kwargs):
        logger.info('User create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('id')
    serializer_class = CustomerSerializer
    permission_classes = [RolePermission]
    def get_permissions(self):
        return [RolePermission(allowed_roles=['admin', 'manager'])]

    def create(self, request, *args, **kwargs):
        logger.info('Customer create requested by user: %s', request.user)
        return super().create(request, *args, **kwargs)
