from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Employee, Customer
from django.contrib.auth.models import User
from .serializers import EmployeeSerializer

class UsersModelTest(TestCase):
    def test_create_employee(self):
        user = User.objects.create(username="emp1")
        emp = Employee.objects.create(user=user, name="Emp1", role="Manager")
        self.assertEqual(emp.name, "Emp1")

    def test_create_customer(self):
        user = User.objects.create(username="cust1")
        cust = Customer.objects.create(user=user, name="Cust1")
        self.assertEqual(cust.name, "Cust1")

class UsersAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        from users.models import Employee
        self.emp = Employee.objects.create(user=self.user, name='Test Admin', role='admin')
        self.client.force_authenticate(user=self.user)
        self.emp_url = reverse('employee-list')
        self.cust_url = reverse('customer-list')

    def test_create_employee(self):
        user2 = User.objects.create_user(username='emp2', password='testpass')
        data = {
            "user_id": user2.id,
            "name": "Emp2",
            "role": "employee"
        }
        response = self.client.post(self.emp_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], "Emp2")

    def test_list_employees(self):
        # Use a new user for the additional Employee to avoid unique constraint violation
        user2 = User.objects.create_user(username='emp2', password='testpass')
        Employee.objects.create(user=user2, name="Emp2", role="manager")
        response = self.client.get(self.emp_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_customer(self):
        user2 = User.objects.create_user(username='cust2', password='testpass')
        data = {
            "user_id": user2.id,
            "name": "Cust2",
            "contact_email": "cust2@example.com"
        }
        response = self.client.post(self.cust_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], "Cust2")

    def test_list_customers(self):
        Customer.objects.create(user=self.user, name="Cust1")
        response = self.client.get(self.cust_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
