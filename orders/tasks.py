from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import requests
import logging
from .models import Order

logger = logging.getLogger(__name__)


@shared_task
def send_order_notifications(order_id):
    """Send SMS to customer and email to admin when order is placed"""
    try:
        order = Order.objects.get(id=order_id)
        
        # Send SMS to customer
        if order.customer.phone_number:
            send_customer_sms.delay(order_id)
        
        # Send email to admin
        send_admin_email.delay(order_id)
        
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")


@shared_task
def send_customer_sms(order_id):
    """Send SMS notification to customer"""
    print(f"Sending SMS for order {order_id}llllllllllllllll") 
    try:
        order = Order.objects.get(id=order_id)
        print(f"Settings: {settings.AFRICAS_TALKING_API_KEY}, {settings.AFRICAS_TALKING_USERNAME}, {settings.AFRICAS_TALKING_SENDER_ID}, {order.customer.phone_number}")  
        
        if not order.customer.phone_number or not settings.AFRICAS_TALKING_API_KEY:
            logger.warning(f"Missing phone number or API key for order {order_id}")
            return
        
        # Format phone number (ensure it starts with +254 for Kenya)
        phone = order.customer.phone_number
        if phone.startswith('0'):
            phone = '+254' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+254' + phone
        
        message = f"Hello {order.customer.first_name}, your order {order.order_number} has been received. Total: KES {order.total_amount}. Thank you for shopping with us!"
        
        # Africa's Talking SMS API
        url = "https://api.sandbox.africastalking.com/version1/messaging"
        headers = {
            'apiKey': settings.AFRICAS_TALKING_API_KEY,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        data = {
            'username': settings.AFRICAS_TALKING_USERNAME,
            'to': phone,
            'message': message,
            'from': settings.AFRICAS_TALKING_SENDER_ID or None,
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 201:
            logger.info(f"SMS sent successfully for order {order_id}")
        else:
            logger.error(f"Failed to send SMS for order {order_id}: {response.text}")
            
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
    except Exception as e:
        logger.error(f"Error sending SMS for order {order_id}: {str(e)}")


@shared_task
def send_admin_email(order_id):
    """Send email notification to admin"""
    try:
        order = Order.objects.get(id=order_id)
        
        subject = f'New Order Received - {order.order_number}'
        
        # Create email context
        context = {
            'order': order,
            'customer': order.customer,
            'items': order.items.all(),
            'site_name': 'E-commerce API',
        }
        
        # Render email templates
        html_message = render_to_string('emails/admin_order_notification.html', context)
        plain_message = render_to_string('emails/admin_order_notification.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        logger.info(f"Admin email sent for order {order_id}")
        
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
    except Exception as e:
        logger.error(f"Error sending admin email for order {order_id}: {str(e)}")
