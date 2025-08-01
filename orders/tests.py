from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem
from suppliers.models import Supplier
from products.models import Product, Category
from users.models import Employee, Customer
from django.contrib.auth.models import User
from warehouses.models import Warehouse, Location
from inventory.models import Stock

class OrdersModelTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Electronics")
        self.prod = Product.objects.create(name="Phone", sku="SKU1", barcode="BAR1", category=self.cat, unit_price=100)
        self.supplier = Supplier.objects.create(name="Acme")
        self.user = User.objects.create(username="emp1")
        self.emp = Employee.objects.create(user=self.user, name="Emp1", role="Manager")
        self.cust_user = User.objects.create(username="cust1")
        self.cust = Customer.objects.create(user=self.cust_user, name="Cust1")
        self.po = PurchaseOrder.objects.create(supplier=self.supplier, created_by=self.emp, status="open")
        self.so = SalesOrder.objects.create(customer=self.cust, created_by=self.emp, status="open")

    def test_purchase_order_item(self):
        poi = PurchaseOrderItem.objects.create(purchase_order=self.po, product=self.prod, quantity=5, unit_price=100)
        self.assertEqual(poi.quantity, 5)

    def test_sales_order_item(self):
        soi = SalesOrderItem.objects.create(sales_order=self.so, product=self.prod, quantity=2, unit_price=100)
        self.assertEqual(soi.quantity, 2)

class OrdersAPITest(APITestCase):
    def setUp(self):
        from rest_framework.test import force_authenticate
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.cat = Category.objects.create(name="Electronics")
        self.prod = Product.objects.create(name="Phone", sku="SKU1", barcode="BAR1", category=self.cat, unit_price=100)
        self.supplier = Supplier.objects.create(name="Acme")
        self.emp = Employee.objects.create(user=self.user, name="Emp1", role="manager")
        self.cust_user = User.objects.create_user(username="cust1", password="testpass")
        self.cust = Customer.objects.create(user=self.cust_user, name="Cust1")
        self.wh = Warehouse.objects.create(name="Main", capacity=1000)
        self.loc = Location.objects.create(warehouse=self.wh, name="A1")
        self.stock = Stock.objects.create(product=self.prod, location=self.loc, quantity=2)
        self.po_url = reverse('purchaseorder-list')
        self.so_url = reverse('salesorder-list')
        self.client.force_authenticate(user=self.user)

    def test_create_purchase_order(self):
        data = {
            "supplier": self.supplier.id,
            "created_by": self.emp.id,
            "status": "open"
        }
        response = self.client.post(self.po_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['supplier'], self.supplier.id)

    def test_list_purchase_orders(self):
        PurchaseOrder.objects.create(supplier=self.supplier, created_by=self.emp, status="open")
        response = self.client.get(self.po_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_sales_order(self):
        data = {
            "customer": self.cust.id,
            "created_by": self.emp.id,
            "status": "open"
        }
        response = self.client.post(self.so_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['customer'], self.cust.id)

    def test_list_sales_orders(self):
        SalesOrder.objects.create(customer=self.cust, created_by=self.emp, status="open")
        response = self.client.get(self.so_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_sales_order_insufficient_stock(self):
        data = {
            "customer": self.cust.id,
            "created_by": self.emp.id,
            "status": "open",
            "items": [
                {"product": self.prod.id, "quantity": 5, "unit_price": 100}
            ]
        }
        response = self.client.post(self.so_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Stock not available", str(response.data))

    def test_stock_deducted_on_sales_order_creation(self):
        initial_stock = self.stock.quantity
        data = {
            "customer": self.cust.id,
            "created_by": self.emp.id,
            "status": "open",
            "items": [
                {"product": self.prod.id, "quantity": 1, "unit_price": 100}
            ]
        }
        response = self.client.post(self.so_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        from inventory.models import Stock
        stock = Stock.objects.get(id=self.stock.id)
        self.assertEqual(stock.quantity, initial_stock - 1)

    def test_stock_increment_on_purchase_order_receipt(self):
        initial_stock = self.stock.quantity
        from orders.models import PurchaseOrder, PurchaseOrderItem
        po = PurchaseOrder.objects.create(supplier=self.supplier, created_by=self.emp, status="open")
        PurchaseOrderItem.objects.create(purchase_order=po, product=self.prod, quantity=3, unit_price=100)
        # Simulate marking PO as received (API or logic to be implemented)
        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse('purchaseorder-receive', args=[po.id])
        response = client.post(url)
        self.assertEqual(response.status_code, 200)
        from inventory.models import Stock
        stock = Stock.objects.get(id=self.stock.id)
        self.assertEqual(stock.quantity, initial_stock + 3)
