from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_user_notification(user_email, order_details):
    subject = 'Your order has been accepted'
    message = f'Your order details: {order_details}'
    send_mail(subject, message, 'from@example.com', [user_email])

@shared_task
def send_master_notification(master_email, payment_details):
    subject = 'Payment received'
    message = f'Payment details: {payment_details}'
    send_mail(subject, message, 'from@example.com', [master_email])