from .serializers import MentorSerializer, MentorAvailabilitySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsMentor
from .models import Mentor, EmailVerificationToken, MentorAvailability
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MentorFilter
from datetime import datetime, date
from rest_framework import status

@api_view(['POST'])
def register_mentor(request):
    """
    Registers a new mentor by accepting their details and creating a Mentor profile.
    The request data should include necessary fields as defined in the MentorSerializer.

    Returns:
        Response: A response containing the created mentor's data or an error message.
    """
    serializer = MentorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsMentor])
def update_mentor_profile(request):
    """
    Updates the profile of the authenticated mentor. The mentor can modify their details
    by providing the updated information in the request data.

    Returns:
        Response: A response containing the updated mentor's data or an error message.
    """
    try:
        mentor_profile = Mentor.objects.get(id=request.user.id)
    except Mentor.DoesNotExist:
        return Response({"error": "Mentor profile not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MentorSerializer(mentor_profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def verify_email(request, token):
    """
    Verifies the mentor's email address using the provided token. If the token is valid
    and has not expired, the mentor's account is activated.

    Args:
        token (str): The email verification token.

    Returns:
        Response: A response indicating the success or failure of the email verification.
    """
    try:
        email_verification_token = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    if email_verification_token.is_valid():
        email_verification_token.user.is_active = True
        email_verification_token.user.save()
        email_verification_token.delete()
        return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
    return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_mentor_list(request):
    """
    Retrieves a list of mentors with optional filtering based on query parameters.
    Supports filtering by fields defined in the MentorFilter.

    Returns:
        Response: A response containing the list of mentors or an error message.
    """
    filter_backends = (DjangoFilterBackend,)
    filterset = MentorFilter(request.GET, queryset=Mentor.objects.all())
    if filterset.is_valid():
        filtered_queryset = filterset.qs
    else:
        return Response({"error": "Invalid filter parameters."}, status=status.HTTP_400_BAD_REQUEST)
    serializer = MentorSerializer(filtered_queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_mentor_detail(request, mentor_id):
    """
    Retrieves the details of a specific mentor identified by their ID.

    Args:
        mentor_id (int): The ID of the mentor.

    Returns:
        Response: A response containing the mentor's data or an error message.
    """
    try:
        mentor = Mentor.objects.get(id=mentor_id)
    except Mentor.DoesNotExist:
        return Response({"detail": "Mentor not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MentorSerializer(mentor)
    return Response(serializer.data)

@api_view(['GET'])
def mentor_availability_list(request, id):
    """
    Retrieves the availability schedule of a specific mentor. The availability can be
    filtered by a specific date provided as a query parameter.

    Args:
        id (int): The ID of the mentor.

    Returns:
        Response: A response containing the mentor's availability or an error message.
    """
    try:
        mentor = Mentor.objects.get(id=id)
    except Mentor.DoesNotExist:
        return Response({"error": "Mentor not found."}, status=status.HTTP_404_NOT_FOUND)

    requested_date = request.query_params.get('date', date.today().strftime('%Y-%m-%d'))

    try:
        datetime.strptime(requested_date, '%Y-%m-%d')
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    availabilities = MentorAvailability.objects.filter(mentor=mentor)
    serializer = MentorAvailabilitySerializer(
        availabilities,
        many=True,
        context={'mentor': mentor, 'date': requested_date}
    )
    return Response(serializer.data)

@api_view(['POST'])
def mentor_availability_create(request):
    """
    Creates or updates the availability slots for the authenticated mentor. The request
    should include a list of availability data, each containing the day of the week,
    start time, and end time.

    Returns:
        Response: A response indicating the success or failure of the operation.
    """
    mentor = request.user
    availability_data = request.data.get('availability', [])

    all_errors = []
    response_data = []
    for slot_data in availability_data:
        serializer = MentorAvailabilitySerializer(data=slot_data, context={'mentor': mentor})

        if serializer.is_valid():
            day_of_week = serializer.validated_data['day_of_week']
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['end_time']

            availability, created = MentorAvailability.objects.update_or_create(
                mentor=mentor, day_of_week=day_of_week,
                defaults={'startTime': start_time, 'end_time': end_time}
            )

            if created:
                message = "Availability created successfully."
            else:
                message = "Availability updated successfully."

            response_data.append({"message": message, "data": serializer.data})

        else:
            all_errors.append(serializer.errors)

    if all_errors:
        return Response({"errors": all_errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"status": "success", "data": response_data}, status=status.HTTP_200_OK)
