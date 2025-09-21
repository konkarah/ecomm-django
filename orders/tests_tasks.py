import pytest
from unittest.mock import patch, Mock
from .tasks import send_customer_sms, send_admin_email


@pytest.mark.django_db
@patch('orders.tasks.requests.post')
def test_send_customer_sms(mock_post, user, product):
    from .models import Order, OrderItem
    
    # Setup
    mock_response = Mock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response
    
    order = Order.objects.create(
        customer=user,
        order_number='SMS-TEST-001'
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        unit_price=product.price
    )
    
    # Test
    send_customer_sms(order.id)
    
    # Assertions
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert 'SMS-TEST-001' in call_args[1]['data']['message']


@pytest.mark.django_db
@patch('orders.tasks.send_mail')
def test_send_admin_email(mock_send_mail, user, product):
    from .models import Order, OrderItem
    
    order = Order.objects.create(
        customer=user,
        order_number='EMAIL-TEST-001'
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        unit_price=product.price
    )
    
    # Test
    send_admin_email(order.id)
    
    # Assertions
    mock_send_mail.assert_called_once()
    call_args = mock_send_mail.call_args[1]
    assert 'EMAIL-TEST-001' in call_args['subject']