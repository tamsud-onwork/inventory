from rest_framework.permissions import BasePermission, SAFE_METHODS

class RolePermission(BasePermission):
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # Allow Django superusers full access
        if hasattr(user, 'is_superuser') and user.is_superuser:
            return True
        # Check for Employee object and role
        employee = getattr(user, 'employee', None)
        if employee and hasattr(employee, 'role'):
            return employee.role in self.allowed_roles
        return False

def role_required(*roles):
    class CustomRolePermission(RolePermission):
        def __init__(self):
            super().__init__(roles)
    return CustomRolePermission,
