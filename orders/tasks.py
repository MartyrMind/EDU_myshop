from io import BytesIO

import weasyprint
from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

from myshop import settings
from orders.models import Order


@shared_task
def order_created(order_id):
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order.id}'
    message = f'Dear {order.first_name},\n\n' \
              f'You have successfully placed an order.' \
              f'Your order ID is {order.id}.'
    mail_sent = send_mail(subject, message, 'admin@myshop.com', [order.email])
    return mail_sent


@shared_task
def payment_completed(order_id):
    """
    Задание по отправке уведомления по электронной почте при успешной оплате заказа
    :param order_id:
    :return:
    """
    order = Order.objects.get(id=order_id)
    # создание электронного письма
    subject = f'My Shop - Invoice no. {order_id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject, message, 'admin@myshop,com', [order.email])
    # генерация PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # прикрепить PDF файл к письму
    email.attach(f'order_{order_id}.pdf', out.getvalue(), 'application/pdf')
    email.send()
