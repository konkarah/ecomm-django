from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer
import uuid


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source='product',
        write_only=True
    )
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'status', 
            'total_amount', 'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'total_amount']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['notes', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        order = Order.objects.create(
            customer=self.context['request'].user,
            order_number=order_number,
            **validated_data
        )
        
        # Create order items
        for item_data in items_data:
            product = item_data['product']
            
            # Check stock availability
            if product.stock_quantity < item_data['quantity']:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
                )
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                unit_price=product.price
            )
            
            # Update stock
            product.stock_quantity -= item_data['quantity']
            product.save()
        
        # Calculate and save total
        order.calculate_total()
        order.save()
        
        return order