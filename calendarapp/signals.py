from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event
from django.conf import settings
from django.core.mail import send_mail


# @receiver(post_save, sender=Mentor)
# def send_verification_email(sender, instance, created, **kwargs):
#     if created and not instance.is_active:
#         send_verification_mail(instance)


# @receiver(post_save, sender=Event)
# def send_room_id_email_on_event_creation(sender, instance, created, **kwargs):
#     if created:
#         room_id = instance.id
#         mentee_email = "vinayak97696@gmail.com"
#
#         subject = "Your Video Call Room ID"
#         message = f"Hello,\n\nYou have been invited to join a video call. Your room ID is: {room_id}\n\nPlease use this room ID to join the call.\n\nBest Regards,\nRaahi"
#         from_email = settings.EMAIL_HOST_USER
#
#         try:
#             send_mail(subject, message, from_email, [mentee_email])
#             print("Email sent successfully.")
#         except Exception as e:
#             print(f"Failed to send email: {e}")
