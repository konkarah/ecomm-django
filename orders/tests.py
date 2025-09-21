import pytest
from django.test import TestCase
from rest_framework import status
from unittest.mock import patch
from .models import Order, OrderItem
from .tasks import send_customer_sms, send_admin_email


class OrderModelTest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from products.models import Category, Product
        
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            price=10.99,
            sku='TEST-001',
            stock_quantity=100
        )
        self.product.categories.add(category)
        
        self.order = Order.objects.create(
            customer=self.user,
            order_number='TEST-ORDER-001'
        )
        
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price=self.product.price
        )
    
    def test_order_creation(self):
        self.assertEqual(self.order.customer, self.user)
        self.assertEqual(self.order.order_number, 'TEST-ORDER-001')
        self.assertEqual(self.order.status, 'pending')
    
    def test_order_item_subtotal(self):
        self.assertEqual(self.order_item.subtotal, 21.98)  # 2 * 10.99
    
    def test_calculate_total(self):
        total = self.order.calculate_total()
        self.assertEqual(total, 21.98)
        self.assertEqual(self.order.total_amount, 21.98)


@pytest.mark.django_db
class TestOrderAPI:
    def test_create_order(self, authenticated_client, product, user):
        data = {
            'notes': 'Test order',
            'items': [
                {
                    'product_id': product.id,
                    'quantity': 2
                }
            ]
        }
        
        response = authenticated_client.post('/api/orders/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['total_amount'] == '21.98'
        
        # Check stock was reduced
        product.refresh_from_db()
        assert product.stock_quantity == 98
    
    def test_insufficient_stock(self, authenticated_client, product):
        product.stock_quantity = 1
        product.save()
        
        data = {
            'items': [
                {
                    'product_id': product.id,
                    'quantity': 5  # More than available stock
                }
            ]
        }
        
        response = authenticated_client.post('/api/orders/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cancel_order(self, authenticated_client, user, product):
        # Create order first
        order = Order.objects.create(
            customer=user,
            order_number='CANCEL-TEST-001'
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            unit_price=product.price
        )
        
        # Reduce stock
        product.stock_quantity = 98
        product.save()
        
        response = authenticated_client.post(f'/api/orders/{order.id}/cancel/')
        assert response.status_code == status.HTTP_200_OK
        
        # Check stock was returned
        product.refresh_from_db()
        assert product.stock_quantity == 100
        
        order.refresh_from_db()
        assert order.status == 'cancelled'