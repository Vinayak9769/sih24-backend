from django.shortcuts import render
from .serializers import MentorSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsMentor
from .models import Mentor
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import EmailVerificationToken
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MentorFilter
from .serializers import MentorAvailabilitySerializer
from .models import MentorAvailability
from datetime import datetime, date
from rest_framework import status


@api_view(['POST'])
def register_mentor(request):
    if request.method == 'POST':
        serializer = MentorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsMentor])
def update_mentor_profile(request):
    try:
        mentor_profile = Mentor.objects.get(id=request.user.id)
    except Mentor.DoesNotExist:
        return Response({"error": "Mentor profile not found."}, status=404)

    serializer = MentorSerializer(mentor_profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
def verify_email(request, token):
    try:
        email_verification_token = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return Response({"error": "Invalid token"}, status=400)

    if email_verification_token.is_valid():
        email_verification_token.user.is_active = True
        email_verification_token.user.save()
        email_verification_token.delete()
        return Response({"message": "Email verified successfully."}, status=200)
    return Response({"error": "Token has expired."}, status=400)


@api_view(['GET'])
def get_mentor_list(request):
    filter_backends = (DjangoFilterBackend,)
    filterset = MentorFilter(request.GET, queryset=Mentor.objects.all())
    if filterset.is_valid():
        filtered_queryset = filterset.qs
    else:
        return Response({"error": "Invalid filter parameters."}, status=400)
    serializer = MentorSerializer(filtered_queryset, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def get_mentor_detail(request, mentor_id):
    try:
        mentor = Mentor.objects.get(id=mentor_id)
    except Mentor.DoesNotExist:
        return Response({"detail": "Mentor not found."}, status=404)

    serializer = MentorSerializer(mentor)
    return Response(serializer.data)


@api_view(['GET'])
def mentor_availability_list(request, id):
    mentor = Mentor.objects.get(id=id)
    requested_date = request.query_params.get('date', date.today().strftime('%Y-%m-%d'))

    try:
        # Validate the date format
        datetime.strptime(requested_date, '%Y-%m-%d')
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    availabilities = MentorAvailability.objects.filter(mentor=mentor)
    serializer = MentorAvailabilitySerializer(
        availabilities,
        many=True,
        context={'mentor': mentor, 'date': requested_date}
    )
    return Response(serializer.data)


@api_view(['POST'])
def mentor_availability_create(request):
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
                defaults={'start_time': start_time, 'end_time': end_time}
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
