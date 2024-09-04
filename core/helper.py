from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import EmailVerificationToken


def send_verification_mail(user):

    if not user.email:
        raise ValidationError("User email is not provided.")

    expiration_time = timezone.now() + timezone.timedelta(hours=24)
    token = EmailVerificationToken.objects.create(user=user, expires_at=expiration_time)
    subject = 'Email Verification'
    verification_link = f'https://localhost:8000/verify/{token.token}/'
    message = f'Please click the following link to verify your email address: {verification_link}'

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        raise ValidationError(f"An error occurred while sending the verification email: {str(e)}")


