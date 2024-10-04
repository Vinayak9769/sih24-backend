from core.permissions import IsMentor
from rest_framework.decorators import api_view, permission_classes
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Mentor, Mentee
from .serializers import EventSerializer, ScheduleMeetingSerializer
from .models import Event
from django_filters.rest_framework import DjangoFilterBackend
from .filters import EventFilters
from icalendar import Calendar
from datetime import datetime, date, time
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .helper import send_room_id_email, send_mail


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMentor])
def create_event(request):
    """
    Creates a new event for a mentor. The request must contain valid event data,
    and the authenticated user must be a mentor. The event is saved in the system
    and associated with the mentor.

    Returns:
        Response: A response containing the event data or an error message.
    """
    try:
        mentor = Mentor.objects.get(id=request.user.id)
    except Mentor.DoesNotExist:
        return Response({"error": "Mentor not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(mentor=mentor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsMentor])
def update_event(request, event_id):
    """
    Updates an existing event created by the mentor. The event is identified by
    the event_id, and the authenticated user must be the mentor who created the event.
    Allows partial updates of the event.

    Args:
        event_id (int): ID of the event to update.

    Returns:
        Response: A response containing the updated event data or an error message.
    """
    try:
        event = Event.objects.get(id=event_id, mentor=request.user.id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found or you do not have permission to edit this event."},
                        status=status.HTTP_404_NOT_FOUND)
    serializer = EventSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsMentor])
def delete_event(request, event_id):
    """
    Deletes an existing event created by the mentor. The event is identified by
    the event_id, and the authenticated user must be the mentor who created the event.

    Args:
        event_id (int): ID of the event to delete.

    Returns:
        Response: A response confirming the deletion or an error message.
    """
    try:
        event = Event.objects.get(id=event_id, mentor=request.user.id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found or you do not have permission to edit this event."},
                        status=status.HTTP_404_NOT_FOUND)
    event.delete()
    return Response({"success": "Event deleted successfully."}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_event_list(request):
    """
    Retrieves a filtered list of events for the authenticated user (mentor).
    The user can filter events using query parameters.

    Returns:
        Response: A response containing the list of events or an error message.
    """
    user = request.user
    filter_backend = DjangoFilterBackend()
    filterset = EventFilters(request.GET,
                             queryset=Event.objects.filter(mentor=user))

    if filterset.is_valid():
        filtered_queryset = filterset.qs
    else:
        return Response({"error": "Invalid filter parameters."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = EventSerializer(filtered_queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMentor])
def upload_ics_view(request):
    """
    Uploads an ICS file and creates events based on the calendar entries in the file.
    The file must be in the ICS format, and the authenticated user must be a mentor.

    Returns:
        Response: A response containing the IDs of the created events or an error message.
    """
    if 'file' not in request.FILES:
        return Response({"detail": "No file provided in the request."}, status=status.HTTP_400_BAD_REQUEST)
    ics_file = request.FILES['file']
    try:
        calendar = Calendar.from_ical(ics_file.read())
        events = []
        mentor = request.user

        for component in calendar.walk():
            if component.name == "VEVENT":
                start_time = component.get('dtstart').dt
                end_time = component.get('dtend').dt
                if isinstance(start_time, datetime):
                    if timezone.is_naive(start_time):
                        start_time = timezone.make_aware(start_time)
                elif isinstance(start_time, date):
                    start_time = timezone.make_aware(datetime.combine(start_time, time.min))

                if isinstance(end_time, datetime):
                    if timezone.is_naive(end_time):
                        end_time = timezone.make_aware(end_time)
                elif isinstance(end_time, date):
                    end_time = timezone.make_aware(datetime.combine(end_time, time.min))
                event = Event.objects.create(
                    mentor=mentor,
                    title=component.get('summary', ''),
                    description=component.get('description', ''),
                    start_time=start_time,
                    end_time=end_time,
                    theme='Personal'
                )
                events.append(event)
        event_ids = [event.id for event in events]
        return Response({"events": event_ids}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def book_event(request):
    """
    Books an event for a mentee with a mentor. The mentee information (name, email, phone)
    and event details (mentor, start time, end time) are provided in the request. An event
    is created and associated with the mentor and mentee. The mentee will receive an email
    with the room ID for the event.

    Returns:
        Response: A response containing the created event data or an error message.
    """
    mentee_data = request.data.get('mentee', {})
    event_data = request.data.get('event', {})

    mentee_email = mentee_data.get('email')
    mentee_name = mentee_data.get('name')
    mentee_phone_number = mentee_data.get('phone_number')
    description = event_data.get('description')
    start_time_str = event_data.get('startDateTime')
    end_time_str = event_data.get('endDateTime')
    mentor_id = event_data.get('mentor')

    if not mentor_id or not start_time_str or not end_time_str:
        return Response({'error': 'Mentor, start time, and end time are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if not mentee_email:
        return Response({'error': 'Mentee email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        mentor = Mentor.objects.get(id=mentor_id)
    except Mentor.DoesNotExist:
        return Response({'error': 'Mentor not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
    except ValueError:
        return Response({'error': 'Invalid datetime format. Use ISO 8601 format with a Z at the end.'},
                        status=status.HTTP_400_BAD_REQUEST)

    mentee, created = Mentee.objects.get_or_create(
        email=mentee_email,
        defaults={
            'name': mentee_name or 'Unknown',
            'phone_number': mentee_phone_number or ''
        }
    )

    event = Event(
        title=f"Meeting with {mentee.name}",
        mentor=mentor,
        mentee=mentee,
        start_time=start_time,
        end_time=end_time,
        description=description or '',
        theme='Meeting'
    )
    event.save()
    serializer = EventSerializer(event)
    send_room_id_email(serializer.data['id'], mentee.email)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
