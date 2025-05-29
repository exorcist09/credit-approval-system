from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Customer, Loan
from datetime import datetime

class RegisterCustomerTest(APITestCase):
    def test_register_customer_success(self):
        url = reverse('register')  
        data = {
            "first_name": "Spider",
            "last_name": "Man",
            "age": 21,
            "monthly_salary": 50000,
            "phone_number": "9876543210"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("data", response.data)

    def test_register_customer_missing_salary(self):
        url = reverse('register')
        data = {
            "first_name": "Peter",
            "last_name": "Parker",
            "age": 21,
            "phone_number": "9876543210"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("monthly_salary", str(response.data))
