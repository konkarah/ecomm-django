# products/serializers.py
from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children', 'full_path', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Category.objects.all(),
        source='categories',
        write_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'sku', 
            'categories', 'category_ids', 'stock_quantity', 
            'is_active', 'created_at', 'updated_at'
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Category.objects.all()
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'sku', 
            'categories', 'stock_quantity', 'is_active'
        ]