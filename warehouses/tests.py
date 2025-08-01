from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Warehouse, Location
from .serializers import WarehouseSerializer
from django.contrib.auth.models import User

class WarehouseModelTest(TestCase):
    def test_create_warehouse(self):
        wh = Warehouse.objects.create(name="Main", capacity=1000)
        self.assertEqual(wh.name, "Main")

    def test_create_location(self):
        wh = Warehouse.objects.create(name="Main", capacity=1000)
        loc = Location.objects.create(warehouse=wh, name="A1")
        self.assertEqual(loc.name, "A1")

class WarehouseAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        from users.models import Employee
        self.emp = Employee.objects.create(user=self.user, name='Test Admin', role='admin')
        self.client.force_authenticate(user=self.user)
        self.warehouse_url = reverse('warehouse-list')

    def test_create_warehouse(self):
        data = {
            "name": "Main",
            "capacity": 1000,
            "address": "123 Main St"
        }
        response = self.client.post(self.warehouse_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], "Main")

    def test_list_warehouses(self):
        Warehouse.objects.create(name="Main", capacity=1000)
        response = self.client.get(self.warehouse_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_warehouse(self):
        wh = Warehouse.objects.create(name="Main", capacity=1000)
        url = reverse('warehouse-detail', args=[wh.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Main")
