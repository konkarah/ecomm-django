from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Customer
from .serializers import CustomerSerializer
from common.pagination import StandardResultsSetPagination


class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        # Only return the current user's data
        return Customer.objects.filter(id=self.request.user.id)