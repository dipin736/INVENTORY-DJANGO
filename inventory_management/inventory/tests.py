from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Item

User = get_user_model()

class ItemTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpassword'
        }).data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.item_data = {
            'name': 'Test Item',
            'description': 'Test description',
            'quantity': 10,
            'price': 100.00
        }
        # Create an item for testing
        self.item = Item.objects.create(**self.item_data)

    def test_create_item(self):
        unique_item_data = {
            'name': 'Unique Test Item',  # Ensure this name is unique
            'description': 'Test description',
            'quantity': 10,
            'price': 100.00
        }
        response = self.client.post(reverse('item_list'), unique_item_data, format='json')
        print(response.data)  # Debugging print
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_item(self):
        response = self.client.get(reverse('item_detail', args=[self.item.id]))
        print(response.data)  # Debugging print
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item(self):
        update_data = {
            'name': 'Updated Item',
            'description': 'Updated description',
            'quantity': 20,
            'price': 200.00
        }
        response = self.client.put(reverse('item_detail', args=[self.item.id]), update_data, format='json')
        print(response.data)  # Debugging print
        self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_delete_item(self):
    self.assertIsNotNone(self.item)  # Check if the item exists
    response = self.client.delete(reverse('item_detail', args=[self.item.id]))  # Ensure this is a DELETE request
    print(response.data)  # Debugging print
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  # Assert for 204 NO CONTENT
