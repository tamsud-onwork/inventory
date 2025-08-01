from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Supplier, SupplierProduct
from products.models import Product, Category
from .serializers import SupplierSerializer
from django.contrib.auth.models import User

class SupplierModelTest(TestCase):
    def test_create_supplier(self):
        sup = Supplier.objects.create(name="Acme")
        self.assertEqual(sup.name, "Acme")

    def test_supplier_product(self):
        sup = Supplier.objects.create(name="Acme")
        cat = Category.objects.create(name="Electronics")
        prod = Product.objects.create(name="Phone", sku="SKU1", barcode="BAR1", category=cat, unit_price=100)
        sp = SupplierProduct.objects.create(supplier=sup, product=prod)
        self.assertEqual(sp.supplier.name, "Acme")

class SupplierAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        from users.models import Employee
        self.emp = Employee.objects.create(user=self.user, name='Test Admin', role='admin')
        self.client.force_authenticate(user=self.user)
        self.supplier_url = reverse('supplier-list')

    def test_create_supplier(self):
        data = {
            "name": "Acme",
            "contact_name": "John Doe",
            "contact_email": "acme@example.com"
        }
        response = self.client.post(self.supplier_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], "Acme")

    def test_list_suppliers(self):
        Supplier.objects.create(name="Acme")
        response = self.client.get(self.supplier_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_supplier(self):
        sup = Supplier.objects.create(name="Acme")
        url = reverse('supplier-detail', args=[sup.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Acme")
