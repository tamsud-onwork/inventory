# Inventory Management System (Django)

## Project Structure
- products: Product, Category, ProductVariant
- suppliers: Supplier, SupplierProduct
- warehouses: Warehouse, Location
- inventory: Stock, StockMovement, StockAdjustment
- orders: PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem
- users: Employee, Customer (extends Django User)

## User Roles & API Access
- Roles are managed in the Employee table (`role` field): `admin`, `manager`, `employee`
- Permissions are enforced per API using a custom permission class and JWT tokens

### Permissions Matrix
| API                  | GET (List/Retrieve)         | POST/PUT/DELETE (Create/Update/Delete) |
|----------------------|-----------------------------|----------------------------------------|
| Products             | All roles                   | Admin, Manager                         |
| Categories           | All roles                   | Admin, Manager                         |
| Product Variants     | All roles                   | Admin, Manager                         |
| Suppliers            | Admin, Manager              | Admin, Manager                         |
| Warehouses           | Admin, Manager              | Admin, Manager                         |
| Inventory/Stock      | Admin, Manager, Employee    | Admin, Manager                         |
| Orders (Purchase)    | Admin, Manager              | Admin, Manager                         |
| Orders (Sales)       | Admin, Manager, Employee    | Admin, Manager, Employee               |
| Employees            | Admin                       | Admin                                  |
| Customers            | Admin, Manager              | Admin, Manager                         |

## JWT Authentication
- Obtain token: `POST /api/token/` with username & password
- Refresh token: `POST /api/token/refresh/` with refresh token
- Use `Authorization: Bearer <access_token>` in headers for all API requests

## How to Change Roles
- Update the `role` field for an Employee in the database or admin panel.
- Example: Set `role` to `admin`, `manager`, or `employee` for the desired user.

## How to Add/Change RBAC for an API
- Edit the relevant viewset in the app's `views.py`.
- Use the `RolePermission` class from `inventory_api.permissions`.
- Example:
```python
from inventory_api.permissions import RolePermission

class ProductViewSet(viewsets.ModelViewSet):
    ...
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [RolePermission(['admin', 'manager'])]
        return [permissions.IsAuthenticated()]
```

## Setup Instructions

### 1. Install Requirements
```powershell
& ".venv/Scripts/python.exe" -m pip install -r requirements.txt
```

### 2. Run Migrations
```powershell
& ".venv/Scripts/python.exe" manage.py makemigrations
& ".venv/Scripts/python.exe" manage.py migrate
```

### 3. Create Superuser (for admin)
```powershell
& ".venv/Scripts/python.exe" manage.py createsuperuser
```

### 4. Load Sample Data
```powershell
& ".venv/Scripts/python.exe" load_sample_data.py
```
- Sample employees created:
  - admin1 / testpass (role: admin)
  - manager1 / testpass (role: manager)
  - employee1 / testpass (role: employee)
- Sample customer: cust1 / testpass

### 5. Run Tests
```powershell
& ".venv/Scripts/python.exe" manage.py test
```

### 6. Run the Application
```powershell
& ".venv/Scripts/python.exe" manage.py runserver
```

- Access the admin at: http://127.0.0.1:8000/admin/
- Login with your superuser or sample employee credentials.

## Test Coverage
- Each app contains model tests in `tests.py`.
- Run all tests as shown above to validate the schema and relationships.

## Data Loading
- The script `load_sample_data.py` will clear and repopulate the database with sample data for all models and roles.

## Demo Sample Data Loader

The `load_sample_data.py` script now:
- Creates multiple categories, products, suppliers, warehouses, and locations.
- Sets up initial stock for several products in different locations.
- Demonstrates business logic:
  - Sales order with insufficient stock (shows error handling)
  - Valid sales order (shows stock deduction)
  - Purchase order receipt (shows stock increment)
  - Stock adjustment as employee (should fail) and as manager (should succeed)
- Prints a summary of all created objects and their states for demo clarity.

**Run this script to quickly reset and demo all advanced business logic scenarios.**

---

## API Documentation (Swagger & Redoc)

Interactive API docs are available after starting the server:

- Swagger UI: [http://127.0.0.1:8000/api/documentation/](http://127.0.0.1:8000/api/documentation/)
- Redoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)
- Raw OpenAPI schema: [http://127.0.0.1:8000/swagger.json](http://127.0.0.1:8000/swagger.json)

You can use these interfaces to explore, test, and document all available API endpoints, including authentication and business logic flows.

---

For further development, add API endpoints and business logic as needed.
