# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.shortcuts import get_object_or_404
# from .models import Order
# from .serializers import OrderSerializer, OrderCreateSerializer
# from .tasks import send_order_notifications


# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_queryset(self):
#         return Order.objects.filter(customer=self.request.user)
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return OrderCreateSerializer
#         return OrderSerializer
    
#     def perform_create(self, serializer):
#         order = serializer.save()
#         # Trigger background task for notifications
#         send_order_notifications.delay(order.id)
#         print(f"Order {order.order_number} created successfully!")
        
#     @action(detail=True, methods=['post'])
#     def cancel(self, request, pk=None):
#         """Cancel an order"""
#         order = self.get_object()
#         if order.status not in ['pending', 'confirmed']:
#             return Response(
#                 {'error': 'Cannot cancel order in current status'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         order.status = 'cancelled'
#         order.save()
        
#         # Return stock
#         for item in order.items.all():
#             item.product.stock_quantity += item.quantity
#             item.product.save()
        
#         return Response({'message': 'Order cancelled successfully'})

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from .tasks import send_order_notifications
from common.pagination import TimestampCursorPagination, StandardResultsSetPagination
import logging

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TimestampCursorPagination  # Orders are time-ordered, cursor pagination works well
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        order = serializer.save()
        try:
            send_order_notifications.delay(order.id)
            logger.info(f"Notification task queued for order {order.id}")
        except Exception as e:
            logger.warning(f"Failed to queue notification task for order {order.id}: {str(e)}")
        
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        if order.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Cannot cancel order in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        # Return stock
        for item in order.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save()
        
        return Response({'message': 'Order cancelled successfully'})



# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.shortcuts import get_object_or_404
# from .models import Order
# from .serializers import OrderSerializer, OrderCreateSerializer
# from .tasks import send_order_notifications
# import logging

# logger = logging.getLogger(__name__)

# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_queryset(self):
#         return Order.objects.filter(customer=self.request.user)
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return OrderCreateSerializer
#         return OrderSerializer
    
#     def perform_create(self, serializer):
#         order = serializer.save()
        
#         # Try to send notifications, but don't fail if Celery is down
#         try:
#             send_order_notifications.delay(order.id)
#             logger.info(f"Notification task queued for order {order.id}")
#         except Exception as e:
#             logger.warning(f"Failed to queue notification task for order {order.id}: {str(e)}")
#             # Order is still created successfully, just no notifications
        
#     @action(detail=True, methods=['post'])
#     def cancel(self, request, pk=None):
#         """Cancel an order"""
#         order = self.get_object()
#         if order.status not in ['pending', 'confirmed']:
#             return Response(
#                 {'error': 'Cannot cancel order in current status'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         order.status = 'cancelled'
#         order.save()
        
#         # Return stock
#         for item in order.items.all():
#             item.product.stock_quantity += item.quantity
#             item.product.save()
        
#         return Response({'message': 'Order cancelled successfully'})