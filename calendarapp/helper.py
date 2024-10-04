from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import TemporaryAccessToken
import icalendar
from .models import Event
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def make_naive(datetime_obj):
    if datetime_obj.tzinfo is not None:
        return datetime_obj.replace(tzinfo=None)
    return datetime_obj


def email_scheduled(mentee, mentor, event):
    token = TemporaryAccessToken.objects.create(event=event, expires_at=event.start_time)
    subject = 'Event Scheduled'
    message = f'Event "{event.title}" has been scheduled with {mentor.first_name} {mentor.last_name} on {event.start_time}.'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [mentee.email, mentor.email])


def convert_ics_to_events(ics_file, mentor):
    events = []
    calendar = icalendar.Calendar.from_ical(ics_file.read())
    for component in calendar.walk():
        if component.name == "VEVENT":
            event = Event(
                mentor=mentor,
                title=str(component.get('summary')),
                description=str(component.get('description', '')),
                start_time=component.get('dtstart').dt,
                end_time=component.get('dtend').dt,
                theme='Personal',
            )
            events.append(event)
    return events

def send_room_id_email(room_id, mentee_email):
    subject = "Your Raahi Video Call Invitation"
    context = {
        'room_link': f"https://localhost:5173/room/1?emailId={mentee_email}&roomId=1"
    }
    html_message = render_to_string('video-call-invitation.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER

    try:
        send_mail(subject, plain_message, from_email, [mentee_email], html_message=html_message)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_meeting_reminder_email(mentee, event):
    mentee_email = mentee.email
    meeting_time = event.start_time
    if meeting_time - timezone.now() < timedelta(minutes=30):
        subject = 'Upcoming Meeting Reminder'
        message = (
            f"Dear {mentee.name},\n\n"
            f"This is a reminder that you have a meeting scheduled with your mentor "
            f"at {meeting_time.strftime('%H:%M')}.\n\n"
            f"Best regards,\nYour Mentor Team"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(
            subject,
            message,
            from_email,
            [mentee_email],
            fail_silently=False,
        )