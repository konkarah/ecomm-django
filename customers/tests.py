import pytest
from django.test import TestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone_number='+254712345678'
        )
    
    def test_customer_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.phone_number, '+254712345678')
        self.assertFalse(self.user.is_verified)
    
    def test_customer_str_representation(self):
        expected = 'Test User'
        self.assertEqual(str(self.user), expected)


@pytest.mark.django_db
class TestCustomerAPI:
    def test_register_customer(self, api_client):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+254787654321'
        }
        
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert 'password' not in response.data
    
    def test_register_password_mismatch(self, api_client):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_profile(self, authenticated_client, user):
        response = authenticated_client.get('/api/auth/profile/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email
    
    def test_update_profile(self, authenticated_client, user):
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+254700000000'
        }
        
        response = authenticated_client.put('/api/auth/profile/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'