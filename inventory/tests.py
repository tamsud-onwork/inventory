from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Stock, StockMovement, StockAdjustment
from products.models import Product, Category
from warehouses.models import Location, Warehouse
from users.models import Employee
from django.contrib.auth.models import User

class InventoryModelTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Electronics")
        self.prod = Product.objects.create(name="Phone", sku="SKU1", barcode="BAR1", category=self.cat, unit_price=100)
        self.wh = Warehouse.objects.create(name="Main", capacity=1000)
        self.loc = Location.objects.create(warehouse=self.wh, name="A1")
        self.stock = Stock.objects.create(product=self.prod, location=self.loc, quantity=10)
        self.user = User.objects.create(username="emp1")
        self.emp = Employee.objects.create(user=self.user, name="Emp1", role="Manager")

    def test_create_stock(self):
        self.assertEqual(self.stock.quantity, 10)

    def test_stock_movement(self):
        move = StockMovement.objects.create(stock=self.stock, movement_type="IN", quantity=5)
        self.assertEqual(move.quantity, 5)

    def test_stock_adjustment(self):
        adj = StockAdjustment.objects.create(stock=self.stock, adjustment_type="ADD", quantity=2, approved_by=self.emp)
        self.assertEqual(adj.quantity, 2)

    def test_negative_stock_quantity(self):
        # Negative: Stock cannot be created with negative quantity
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            Stock.objects.create(product=self.prod, location=self.loc, quantity=-5)

    def test_duplicate_stock(self):
        # Negative: Duplicate stock for same product/location should raise error if unique constraint
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            Stock.objects.create(product=self.prod, location=self.loc, quantity=10)
        with self.assertRaises(ValidationError):
            Stock.objects.create(product=self.prod, location=self.loc, quantity=5)

class StockAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.emp = Employee.objects.create(user=self.user, name='Test User', role='manager')
        self.client.force_authenticate(user=self.user)
        self.cat = Category.objects.create(name="Electronics")
        self.prod = Product.objects.create(name="Phone", sku="SKU1", barcode="BAR1", category=self.cat, unit_price=100)
        self.wh = Warehouse.objects.create(name="Main", capacity=1000)
        self.loc = Location.objects.create(warehouse=self.wh, name="A1")
        self.stock_url = reverse('stock-list')

    def test_update_stock(self):
        stock = Stock.objects.create(product=self.prod, location=self.loc, quantity=10)
        url = reverse('stock-detail', args=[stock.id])
        data = {"quantity": 20}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['quantity'], 20)

    def test_update_stock_negative_quantity(self):
        stock = Stock.objects.create(product=self.prod, location=self.loc, quantity=10)
        url = reverse('stock-detail', args=[stock.id])
        data = {"quantity": -5}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('quantity', response.data)

    def test_update_stock_duplicate(self):
        stock1 = Stock.objects.create(product=self.prod, location=self.loc, quantity=10)
        # Try to update another stock to same product/location (should fail if unique constraint)
        wh2 = Warehouse.objects.create(name="Secondary", capacity=500)
        loc2 = Location.objects.create(warehouse=wh2, name="B1")
        stock2 = Stock.objects.create(product=self.prod, location=loc2, quantity=5)
        url = reverse('stock-detail', args=[stock2.id])
        data = {"product": self.prod.id, "location": self.loc.id}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)

    def test_delete_nonexistent_stock(self):
        url = reverse('stock-detail', args=[9999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_list_stock_empty(self):
        response = self.client.get(self.stock_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_permission_denied_for_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {"product": self.prod.id, "location": self.loc.id, "quantity": 10}
        response = self.client.post(self.stock_url, data)
        self.assertEqual(response.status_code, 401)

    def test_permission_denied_for_wrong_method(self):
        # PATCH on list endpoint should fail
        response = self.client.patch(self.stock_url, {"quantity": 5})
        self.assertEqual(response.status_code, 405)

    def test_delete_stock(self):
        stock = Stock.objects.create(product=self.prod, location=self.loc, quantity=10)
        url = reverse('stock-detail', args=[stock.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_permission_denied_for_non_manager(self):
        # User with no manager/admin role should not be able to create stock
        user2 = User.objects.create_user(username='user2', password='testpass')
        self.client.force_authenticate(user=user2)
        data = {"product": self.prod.id, "location": self.loc.id, "quantity": 10}
        response = self.client.post(self.stock_url, data)
        self.assertEqual(response.status_code, 403)

    def test_create_stock(self):
        data = {
            "product": self.prod.id,
            "location": self.loc.id,
            "quantity": 10
        }
        response = self.client.post(self.stock_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['quantity'], 10)

    def test_list_stock(self):
        Stock.objects.create(product=self.prod, location=self.loc, quantity=10)
        response = self.client.get(self.stock_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_stock(self):
        stock = Stock.objects.create(product=self.prod, location=self.loc, quantity=10)
        url = reverse('stock-detail', args=[stock.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['quantity'], 10)

    def test_create_stock_invalid_data(self):
        # Negative: missing product
        data = {"location": self.loc.id, "quantity": 10}
        response = self.client.post(self.stock_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('product', response.data)

        # Negative: negative quantity
        data = {"product": self.prod.id, "location": self.loc.id, "quantity": -10}
        response = self.client.post(self.stock_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('quantity', response.data)

class StockAdjustmentApprovalTest(APITestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Electronics")
        self.prod = Product.objects.create(name="Phone", sku="SKU1", barcode="BAR1", category=self.cat, unit_price=100)
        self.wh = Warehouse.objects.create(name="Main", capacity=1000)
        self.loc = Location.objects.create(warehouse=self.wh, name="A1")
        self.stock = Stock.objects.create(product=self.prod, location=self.loc, quantity=10)
        self.admin_user = User.objects.create_user(username='admin1', password='testpass')
        self.admin_emp = Employee.objects.create(user=self.admin_user, name='Admin1', role='admin')
        self.manager_user = User.objects.create_user(username='manager1', password='testpass')
        self.manager_emp = Employee.objects.create(user=self.manager_user, name='Manager1', role='manager')
        self.employee_user = User.objects.create_user(username='employee1', password='testpass')
        self.employee_emp = Employee.objects.create(user=self.employee_user, name='Employee1', role='employee')
        self.url = reverse('stockadjustment-list')

    def test_adjustment_negative_quantity(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "stock": self.stock.id,
            "adjustment_type": "ADD",
            "quantity": -5,
            "reason": "Correction",
            "approved_by": self.admin_emp.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('quantity', response.data)

    def test_employee_cannot_approve_stock_adjustment(self):
        self.client.force_authenticate(user=self.employee_user)
        data = {
            "stock": self.stock.id,
            "adjustment_type": "ADD",
            "quantity": 5,
            "reason": "Correction",
            "approved_by": self.employee_emp.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_manager_can_approve_stock_adjustment(self):
        self.client.force_authenticate(user=self.manager_user)
        data = {
            "stock": self.stock.id,
            "adjustment_type": "ADD",
            "quantity": 5,
            "reason": "Correction",
            "approved_by": self.manager_emp.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertIn(response.status_code, [200, 201])

    def test_admin_can_approve_stock_adjustment(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "stock": self.stock.id,
            "adjustment_type": "ADD",
            "quantity": 5,
            "reason": "Correction",
            "approved_by": self.admin_emp.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertIn(response.status_code, [200, 201])

    def test_stock_adjustment_invalid_data(self):
        self.client.force_authenticate(user=self.admin_user)
        # Negative: missing required fields
        data = {"stock": "", "adjustment_type": "", "quantity": "", "approved_by": ""}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('stock', response.data)
        self.assertIn('adjustment_type', response.data)
        self.assertIn('quantity', response.data)

    def test_adjustment_for_nonexistent_stock(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "stock": 9999,
            "adjustment_type": "ADD",
            "quantity": 5,
            "reason": "Correction",
            "approved_by": self.admin_emp.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('stock', response.data)

    def test_adjustment_with_invalid_approved_by(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "stock": self.stock.id,
            "adjustment_type": "ADD",
            "quantity": 5,
            "reason": "Correction",
            "approved_by": 9999
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('approved_by', response.data)

    def test_adjustment_with_invalid_type(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "stock": self.stock.id,
            "adjustment_type": "INVALID",
            "quantity": 5,
            "reason": "Correction",
            "approved_by": self.admin_emp.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('adjustment_type', response.data)
