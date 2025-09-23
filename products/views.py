# products/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Avg
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductCreateSerializer
from common.pagination import StandardResultsSetPagination, LargeResultsSetPagination, SmallResultsSetPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = SmallResultsSetPagination  # Categories don't need large pagination
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products in this category and its subcategories"""
        category = self.get_object()
        all_categories = [category] + category.get_all_children()
        products = Product.objects.filter(categories__in=all_categories, is_active=True).distinct()
        
        # Apply pagination to the action
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = LargeResultsSetPagination  # Products can have many items
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Bulk upload products - no pagination needed for creation"""
        if not isinstance(request.data, list):
            return Response(
                {'error': 'Expected a list of products'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ProductCreateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryAveragePriceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, category_id):
        """Get average product price for a given category"""
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all subcategories
        all_categories = [category] + category.get_all_children()
        
        # Calculate average price
        avg_price = Product.objects.filter(
            categories__in=all_categories,
            is_active=True
        ).aggregate(avg_price=Avg('price'))['avg_price']
        
        return Response({
            'category': category.name,
            'category_path': category.get_full_path(),
            'average_price': round(avg_price, 2) if avg_price else 0,
            'total_products': Product.objects.filter(
                categories__in=all_categories,
                is_active=True
            ).count()
        })