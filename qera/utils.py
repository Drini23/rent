from django.core.mail import send_mail
from django.conf import settings

def send_payment_email(user_email, username, amount, reservation_id, reservation_car):
    subject = "Payment Confirmation"
    message = f"""
    Dear {username},

    Thank you for your payment for reservation ID {reservation_id}. and Model Car {reservation_car}
    The total amount of ${amount:.2f} has been successfully received.

    We appreciate your business!

    Best regards,
    The Car Rental Team
    """
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    # Send the email and return the result
    result = send_mail(subject, message, from_email, recipient_list)
    return result
