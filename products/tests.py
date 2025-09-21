import pytest
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Category, Product

User = get_user_model()


class CategoryModelTest(TestCase):
    def setUp(self):
        self.root_category = Category.objects.create(name='All Products')
        self.parent_category = Category.objects.create(
            name='Electronics', 
            parent=self.root_category
        )
        self.child_category = Category.objects.create(
            name='Smartphones', 
            parent=self.parent_category
        )
    
    def test_category_creation(self):
        self.assertEqual(self.root_category.name, 'All Products')
        self.assertIsNone(self.root_category.parent)
    
    def test_category_hierarchy(self):
        self.assertEqual(self.child_category.parent, self.parent_category)
        self.assertEqual(self.parent_category.parent, self.root_category)
    
    def test_get_full_path(self):
        expected_path = 'All Products > Electronics > Smartphones'
        self.assertEqual(self.child_category.get_full_path(), expected_path)
    
    def test_get_all_children(self):
        children = self.root_category.get_all_children()
        self.assertIn(self.parent_category, children)
        self.assertIn(self.child_category, children)


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=19.99,
            sku='TEST-001',
            stock_quantity=50
        )
        self.product.categories.add(self.category)
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, 19.99)
        self.assertEqual(self.product.stock_quantity, 50)
        self.assertTrue(self.product.is_active)
    
    def test_product_categories(self):
        self.assertIn(self.category, self.product.categories.all())


@pytest.mark.django_db
class TestCategoryAPI:
    def test_list_categories(self, authenticated_client):
        Category.objects.create(name='Test Category')
        
        response = authenticated_client.get('/api/products/categories/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_create_category(self, authenticated_client):
        data = {'name': 'New Category'}
        
        response = authenticated_client.post('/api/products/categories/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Category'
    
    def test_category_average_price(self, authenticated_client, category, product):
        response = authenticated_client.get(f'/api/products/categories/{category.id}/average-price/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['average_price'] == 10.99


@pytest.mark.django_db
class TestProductAPI:
    def test_list_products(self, authenticated_client, product):
        response = authenticated_client.get('/api/products/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_create_product(self, authenticated_client, category):
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '25.99',
            'sku': 'NEW-001',
            'categories': [category.id],
            'stock_quantity': 75
        }
        
        response = authenticated_client.post('/api/products/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Product'
    
    def test_bulk_upload_products(self, authenticated_client, category):
        data = [
            {
                'name': 'Product 1',
                'description': 'Description 1',
                'price': '10.00',
                'sku': 'BULK-001',
                'categories': [category.id],
                'stock_quantity': 10
            },
            {
                'name': 'Product 2',
                'description': 'Description 2',
                'price': '20.00',
                'sku': 'BULK-002',
                'categories': [category.id],
                'stock_quantity': 20
            }
        ]
        
        response = authenticated_client.post('/api/products/bulk_upload/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2