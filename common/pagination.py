from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for most endpoints
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.page.paginator.per_page),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for large datasets (products, orders)
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.page.paginator.per_page),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('has_next', self.page.has_next()),
            ('has_previous', self.page.has_previous()),
            ('results', data)
        ]))


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for small datasets (categories)
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class OffsetLimitPagination(LimitOffsetPagination):
    """
    Offset-based pagination for APIs that need skip/take patterns
    """
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('limit', self.limit),
            ('offset', self.offset),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class TimestampCursorPagination(CursorPagination):
    """
    Cursor pagination for time-ordered data (orders, logs)
    Best for real-time data that changes frequently
    """
    page_size = 20
    ordering = '-created_at'  # Must have an ordering field
    cursor_query_param = 'cursor'
    page_size_query_param = 'page_size'
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))