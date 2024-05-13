import logging

import requests
from django.conf import settings
from django.core.mail import send_mail

from apps.products.models import Order
from mini_market.celery import app as celery

logger = logging.getLogger(__name__)


@celery.task()
def payment(order_id):
    try:
        order = Order.objects.select_related('user').get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f'Order with id "{order_id}" not found.')
        return

    send_data = {
        'amount': float(order.total_cost),
        'items_qty': order.quantity,
        'api_token': settings.PAYMENT_TOKEN,
        'user_email': order.user.email,
    }
    response = requests.post(settings.PAYMENT_URL, json=send_data)

    if response.status_code != 200:
        logger.error(
            f'Request to payment service fail: url "{settings.PAYMENT_URL}"'
        )
        return

    data = response.json()
    order.order_id = data['orderId']
    order.payment_url = data['url']
    order.save()

    send_mail(
        subject='Ссылка на оплату заказа Mini Market',
        message=f'Для оплаты заказа перейдите по ссылке: {data["url"]}',
        recipient_list=(order.user.email,),
        from_email=settings.EMAIL_HOST_USER,
        fail_silently=False,
        connection=None,
        html_message=None,
    )
