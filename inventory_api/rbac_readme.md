# RBAC & JWT Setup

## JWT Authentication
- Obtain token: `POST /api/token/` with username & password
- Refresh token: `POST /api/token/refresh/` with refresh token
- Use `Authorization: Bearer <access_token>` in headers for all API requests

## Role-Based Access Control (RBAC)
- Roles are managed in the Employee table (`role` field)
- Roles: `admin`, `manager`, `employee`
- Permissions are enforced per API using a custom permission class

## Example Permissions
| API                  | GET (List/Retrieve) | POST/PUT/DELETE (Create/Update/Delete) |
|----------------------|---------------------|----------------------------------------|
| Products             | All roles           | Admin, Manager                         |
| Categories           | All roles           | Admin, Manager                         |
| Product Variants     | All roles           | Admin, Manager                         |
| Suppliers            | Admin, Manager      | Admin, Manager                         |
| Warehouses           | Admin, Manager      | Admin, Manager                         |
| Inventory/Stock      | Admin, Manager, Employee | Admin, Manager                    |
| Orders (Purchase)    | Admin, Manager      | Admin, Manager                         |
| Orders (Sales)       | Admin, Manager, Employee | Admin, Manager, Employee           |
| Employees            | Admin               | Admin                                  |
| Customers            | Admin, Manager      | Admin, Manager                         |

## How to Add/Change Roles
- Update the `role` field for an Employee in the database or admin panel.

## How to Add RBAC to a View
```
from inventory_api.permissions import RolePermission

class ProductViewSet(viewsets.ModelViewSet):
    ...
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [RolePermission(['admin', 'manager'])]
        return [permissions.IsAuthenticated()]
```
