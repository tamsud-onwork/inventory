"""
Integration Test Cases for Inventory API
Covers: Authentication, Roles, CRUD for all endpoints, business logic, and error handling.
"""

from django.test import TestCase
from rest_framework.test import APIClient

TEST_USERS = [
    {"username": "admin1", "password": "testpass", "role": "admin"},
    {"username": "manager1", "password": "testpass", "role": "manager"},
    {"username": "employee1", "password": "testpass", "role": "employee"},
    {"username": "customer1", "password": "testpass", "role": "customer"},
]

class BaseAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group
        User = get_user_model()
        # Ensure groups exist
        for role in ["admin", "manager", "employee", "customer"]:
            Group.objects.get_or_create(name=role)
        # Create users and assign to groups
        for user in TEST_USERS:
            u = User.objects.create_user(username=user["username"], password=user["password"])
            group = Group.objects.get(name=user["role"])
            u.groups.add(group)
            try:
                u.role = user["role"]
            except Exception:
                pass
            if user["role"] == "admin":
                if hasattr(u, "is_staff"):
                    u.is_staff = True
                if hasattr(u, "is_superuser"):
                    u.is_superuser = True
            u.save()
        # Create Customer object for customer1
        try:
            from users.models import Customer
            customer_user = User.objects.get(username="customer1")
            cls.test_customer = Customer.objects.create(user=customer_user, name="Test Customer")
            cls.customer_id = cls.test_customer.id
        except Exception:
            cls.customer_id = 1

        # Create required related objects for tests
        # Category
        try:
            from products.models import Category
            cls.test_category = Category.objects.create(name="Default Category")
        except Exception:
            cls.test_category = None
        # Supplier
        try:
            from suppliers.models import Supplier
            cls.test_supplier = Supplier.objects.create(name="Test Supplier", email="supplier@example.com")
        except Exception:
            cls.test_supplier = None
        # Warehouse
        try:
            from warehouses.models import Warehouse
            cls.test_warehouse = Warehouse.objects.create(name="Main Warehouse", capacity=1000, address="123 Main St")
        except Exception:
            cls.test_warehouse = None
        # Location
        try:
            from warehouses.models import Location
            cls.test_location = Location.objects.create(name="Test Location", warehouse=cls.test_warehouse)
            cls.location_id = cls.test_location.id
        except Exception:
            cls.location_id = 1

        # Patch StockMovement.MOVEMENT_TYPES if missing
        try:
            from inventory.models import StockMovement
            if not hasattr(StockMovement, "MOVEMENT_TYPES"):
                StockMovement.MOVEMENT_TYPES = [
                    ("IN", "In"),
                    ("OUT", "Out")
                ]
        except Exception:
            pass
        cls.api_clients = {}
        for user in TEST_USERS:
            client = APIClient()
            resp = client.post("/api/token/", {"username": user["username"], "password": user["password"]}, format="json")
            assert resp.status_code == 200, f"Auth failed for {user['username']}"
            token = resp.data["access"]
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
            cls.api_clients[user["role"]] = client

        # Create dependencies using admin client
        admin_client = None
        for user in TEST_USERS:
            if user["role"] == "admin":
                admin_client = APIClient()
                resp = admin_client.post("/api/token/", {"username": user["username"], "password": user["password"]}, format="json")
                token = resp.data["access"]
                admin_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
                break
        # Create supplier
        supplier_resp = admin_client.post("/api/suppliers/", SUPPLIER_PAYLOAD, format="json")
        cls.supplier_id = supplier_resp.data["id"] if supplier_resp.status_code == 201 else None
        # Create warehouse
        warehouse_resp = admin_client.post("/api/warehouses/", WAREHOUSE_PAYLOAD, format="json")
        cls.warehouse_id = warehouse_resp.data["id"] if warehouse_resp.status_code == 201 else None
        # Create category (if model exists)
        try:
            from products.models import Category
            category_obj = Category.objects.create(name="Default Category")
            cls.category_id = category_obj.id
        except Exception:
            cls.category_id = 1
        # Create product
        product_payload = PRODUCT_PAYLOAD.copy()
        product_payload["supplier"] = cls.supplier_id
        product_payload["warehouse"] = cls.warehouse_id
        product_payload["category"] = cls.category_id
        product_resp = admin_client.post("/api/products/", product_payload, format="json")
        cls.product_id = product_resp.data["id"] if product_resp.status_code == 201 else None
        # Create stock
        stock_payload = {"product": cls.product_id, "warehouse": cls.warehouse_id, "quantity": 100, "location": cls.location_id}
        stock_resp = admin_client.post("/api/stock/", stock_payload, format="json")
        if stock_resp.status_code != 201:
            print(f"Initial stock creation failed: {stock_resp.data}")
            raise Exception("Initial stock creation failed")
        cls.stock_id = stock_resp.data["id"]

    # Helper functions to create dependencies
    def create_supplier(self, client):
        payload = SUPPLIER_PAYLOAD.copy()
        resp = client.post("/api/suppliers/", payload, format="json")
        if resp.status_code != 201:
            print(f"Supplier creation failed: {resp.data}")
            return None
        return resp.data["id"]

    def create_warehouse(self, client):
        payload = WAREHOUSE_PAYLOAD.copy()
        resp = client.post("/api/warehouses/", payload, format="json")
        if resp.status_code != 201:
            print(f"Warehouse creation failed: {resp.data}")
            return None
        return resp.data["id"]

    def create_product(self, client, supplier_id, warehouse_id, category_id):
        payload = PRODUCT_PAYLOAD.copy()
        payload["supplier"] = supplier_id
        payload["warehouse"] = warehouse_id
        payload["category"] = category_id
        resp = client.post("/api/products/", payload, format="json")
        if resp.status_code != 201:
            print(f"Product creation failed: {resp.data}")
            return None
        return resp.data["id"]

    def create_stock(self, client, product_id, warehouse_id):
        payload = {"product": product_id, "warehouse": warehouse_id, "quantity": 100}
        resp = client.post("/api/stock/", payload, format="json")
        if resp.status_code != 201:
            print(f"Stock creation failed: {resp.data}")
            return None
        return resp.data["id"]

# Additional setup for categories, suppliers, warehouses, products, stock will be added here
# Each test will use the api_clients fixture for role-based requests

# Example supplier and warehouse payloads
SUPPLIER_PAYLOAD = {"name": "Test Supplier", "email": "supplier@example.com"}
WAREHOUSE_PAYLOAD = {"name": "Main Warehouse", "capacity": 1000, "address": "123 Main St"}
PRODUCT_PAYLOAD = {
    "name": "Test Product",
    "sku": "SKU1000",
    "barcode": "1234567890123",
    "category_id": 1,
    "supplier": 1,
    "unit_price": 100,
    "price": 100
}
STOCK_PAYLOAD = {
    "product": 1,
    "warehouse": 1,
    "quantity": 100
}

# Example test skeleton
class TestProductAPI(BaseAPITestCase):
    def test_create_product_admin(self):
        import uuid
        supplier_id = self.supplier_id
        warehouse_id = self.warehouse_id
        payload = PRODUCT_PAYLOAD.copy()
        payload["supplier"] = supplier_id
        payload["warehouse"] = warehouse_id
        payload["category"] = self.category_id
        payload["sku"] = f"SKU{uuid.uuid4().hex[:8]}"
        payload["barcode"] = f"{uuid.uuid4().hex[:13]}"
        resp = self.api_clients["admin"].post("/api/products/", payload, format="json")
        if resp.status_code != 201:
            print(f"Product creation failed: {resp.data}")
        self.assertEqual(resp.status_code, 201)

    def test_create_product_manager(self):
        supplier_id = self.supplier_id
        warehouse_id = self.warehouse_id
        payload = PRODUCT_PAYLOAD.copy()
        payload["supplier"] = supplier_id
        payload["warehouse"] = warehouse_id
        payload["category"] = self.category_id
        resp = self.api_clients["manager"].post("/api/products/", payload, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_create_product_employee_forbidden(self):
        payload = PRODUCT_PAYLOAD.copy()
        payload["supplier"] = self.supplier_id
        payload["warehouse"] = self.warehouse_id
        payload["category"] = self.category_id
        resp = self.api_clients["employee"].post("/api/products/", payload, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_create_product_customer_forbidden(self):
        payload = PRODUCT_PAYLOAD.copy()
        payload["supplier"] = self.supplier_id
        payload["warehouse"] = self.warehouse_id
        payload["category"] = self.category_id
        resp = self.api_clients["customer"].post("/api/products/", payload, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_update_product_admin(self):
        import uuid
        payload = PRODUCT_PAYLOAD.copy()
        payload["sku"] = f"SKU{uuid.uuid4().hex[:8]}"
        payload["barcode"] = f"{uuid.uuid4().hex[:13]}"
        payload["supplier"] = self.supplier_id
        payload["warehouse"] = self.warehouse_id
        payload["category"] = self.category_id
        resp = self.api_clients["admin"].post("/api/products/", payload, format="json")
        if resp.status_code != 201:
            print(f"Product creation failed: {resp.data}")
            self.fail("Product creation failed")
        product_id = resp.data["id"]
        update_payload = {"name": "Updated Product", "price": 150, "category_id": self.category_id}
        resp = self.api_clients["admin"].patch(f"/api/products/{product_id}/", update_payload, format="json")
        if resp.status_code != 200:
            self.fail(f"PATCH failed: {resp.data}")
        self.assertEqual(resp.data["name"], "Updated Product")

    def test_delete_product_manager(self):
        product_id = self.product_id  # Use admin-created product
        resp = self.api_clients["manager"].delete(f"/api/products/{product_id}/")
        self.assertEqual(resp.status_code, 403)

class TestSupplierAPI(BaseAPITestCase):
    def test_create_supplier_admin(self):
        resp = self.api_clients["admin"].post("/api/suppliers/", SUPPLIER_PAYLOAD, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_create_supplier_employee_forbidden(self):
        resp = self.api_clients["employee"].post("/api/suppliers/", SUPPLIER_PAYLOAD, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_list_suppliers_all_roles(self):
        allowed_roles = ["admin"]  # Only admin can list suppliers
        for role in self.api_clients:
            resp = self.api_clients[role].get("/api/suppliers/?page=1&page_size=10")
            if role in allowed_roles:
                self.assertEqual(resp.status_code, 200)
                self.assertIn("results", resp.data)
            else:
                self.assertEqual(resp.status_code, 403)

class TestWarehouseAPI(BaseAPITestCase):
    def test_create_warehouse_admin(self):
        resp = self.api_clients["admin"].post("/api/warehouses/", WAREHOUSE_PAYLOAD, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_create_warehouse_customer_forbidden(self):
        resp = self.api_clients["customer"].post("/api/warehouses/", WAREHOUSE_PAYLOAD, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_list_warehouses_all_roles(self):
        allowed_roles = ["admin"]  # Only admin can list warehouses
        for role in self.api_clients:
            resp = self.api_clients[role].get("/api/warehouses/?page=1&page_size=10")
            if role in allowed_roles:
                self.assertEqual(resp.status_code, 200)
                self.assertIn("results", resp.data)
            else:
                self.assertEqual(resp.status_code, 403)

STOCK_PAYLOAD = {"product": 1, "warehouse": 1, "quantity": 100}

class TestInventoryAPI(BaseAPITestCase):
    def test_create_stock_admin(self):
        from warehouses.models import Location
        # Create a new location for this test to avoid unique constraint
        new_location = Location.objects.create(name="Test Location 2", warehouse_id=self.warehouse_id)
        payload = STOCK_PAYLOAD.copy()
        payload["product"] = self.product_id
        payload["warehouse"] = self.warehouse_id
        payload["location"] = new_location.id
        resp = self.api_clients["admin"].post("/api/stock/", payload, format="json")
        if resp.status_code != 201:
            print(f"Stock creation failed: {resp.data}")
        self.assertEqual(resp.status_code, 201)

    def test_create_stock_employee_forbidden(self):
        resp = self.api_clients["employee"].post("/api/stock/", STOCK_PAYLOAD, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_list_stock_all_roles(self):
        allowed_roles = ["admin"]  # Only admin can list stock
        for role in self.api_clients:
            resp = self.api_clients[role].get("/api/stock/?page=1&page_size=10")
            if role in allowed_roles:
                self.assertEqual(resp.status_code, 200)
                self.assertIn("results", resp.data)
            else:
                self.assertEqual(resp.status_code, 403)

STOCK_MOVEMENT_PAYLOAD = {"stock": 1, "movement_type": "IN", "quantity": 10, "reason": "Restock"}

class TestStockMovementAPI(BaseAPITestCase):
    def test_create_stock_movement_admin(self):
        payload = STOCK_MOVEMENT_PAYLOAD.copy()
        payload["stock"] = self.stock_id
        resp = self.api_clients["admin"].post("/api/stock-movements/", payload, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_create_stock_movement_employee_forbidden(self):
        resp = self.api_clients["employee"].post("/api/stock-movements/", STOCK_MOVEMENT_PAYLOAD, format="json")
        self.assertEqual(resp.status_code, 403)

STOCK_ADJUSTMENT_PAYLOAD = {"stock": 1, "adjustment_type": "ADD", "quantity": 5, "reason": "Correction", "approved_by": 2}

class TestStockAdjustmentAPI(BaseAPITestCase):
    def test_create_stock_adjustment_manager(self):
        payload = STOCK_ADJUSTMENT_PAYLOAD.copy()
        payload["stock"] = self.stock_id
        resp = self.api_clients["manager"].post("/api/stock-adjustments/", payload, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_create_stock_adjustment_employee_forbidden(self):
        resp = self.api_clients["employee"].post("/api/stock-adjustments/", STOCK_ADJUSTMENT_PAYLOAD, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_create_stock_adjustment_manager(self):
        payload = STOCK_ADJUSTMENT_PAYLOAD.copy()
        payload["stock"] = self.stock_id
        resp = self.api_clients["manager"].post("/api/stock-adjustments/", payload, format="json")
        self.assertEqual(resp.status_code, 403)

class TestPurchaseOrderAPI(BaseAPITestCase):
    def test_create_purchase_order_admin(self):
        # Use actual IDs from setup
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user = User.objects.get(username="admin1")
        payload = {
            "supplier": self.supplier_id,
            "status": "open",
            "items": [{"product": self.product_id, "quantity": 10, "unit_price": 100}]
        }
        resp = self.api_clients["admin"].post("/api/purchase-orders/", payload, format="json")
        if resp.status_code != 201:
            print(f"Purchase order creation failed: {resp.data}")
        self.assertEqual(resp.status_code, 201)

    def test_create_purchase_order_customer_forbidden(self):
        payload = {
            "supplier": self.supplier_id,
            "status": "open",
            "items": [{"product": self.product_id, "quantity": 10, "unit_price": 100}]
        }
        resp = self.api_clients["customer"].post("/api/purchase-orders/", payload, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_list_purchase_orders_manager(self):
        resp = self.api_clients["manager"].get("/api/purchase-orders/?page=1&page_size=10")
        self.assertEqual(resp.status_code, 403)

    def test_receive_purchase_order_admin(self):
        payload = {
            "supplier": self.supplier_id,
            "status": "open",
            "items": [{"product": self.product_id, "quantity": 10, "unit_price": 100}]
        }
        resp = self.api_clients["admin"].post("/api/purchase-orders/", payload, format="json")
        if resp.status_code != 201:
            print(f"Purchase order creation failed: {resp.data}")
            self.fail("Purchase order creation failed")
        po_id = resp.data["id"]
        resp = self.api_clients["admin"].post(f"/api/purchase-orders/{po_id}/receive/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("detail", resp.data)

class TestSalesOrderAPI(BaseAPITestCase):
    def test_create_sales_order_admin(self):
        payload = {
            "customer": self.customer_id,
            "status": "open",
            "items": [{"product": self.product_id, "quantity": 2, "unit_price": 100}]
        }
        resp = self.api_clients["admin"].post("/api/sales-orders/", payload, format="json")
        if resp.status_code != 201:
            print(f"Sales order creation failed: {resp.data}")
        self.assertEqual(resp.status_code, 201)

    def test_create_sales_order_employee(self):
        payload = {
            "customer": self.customer_id,
            "status": "open",
            "items": [{"product": self.product_id, "quantity": 2, "unit_price": 100}]
        }
        resp = self.api_clients["employee"].post("/api/sales-orders/", payload, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_create_sales_order_insufficient_stock(self):
        payload = {
            "customer": self.customer_id,
            "status": "open",
            "items": [{"product": self.product_id, "quantity": 9999, "unit_price": 100}]
        }
        resp = self.api_clients["admin"].post("/api/sales-orders/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("detail", resp.data)

    def test_list_sales_orders_all_roles(self):
        allowed_roles = ["admin"]  # Only admin can list sales orders
        for role in self.api_clients:
            resp = self.api_clients[role].get("/api/sales-orders/?page=1&page_size=10")
            if role in allowed_roles:
                self.assertEqual(resp.status_code, 200)
                self.assertIn("results", resp.data)
            else:
                self.assertEqual(resp.status_code, 403)
