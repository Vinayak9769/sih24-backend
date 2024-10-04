from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.shortcuts import get_object_or_404
from core.models import Mentor, CalendlyToken
from calendarapp.models import Event
from calendarapp.serializers import EventSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone


class CalendlyAuthView(APIView):
    """
    View to generate the Calendly OAuth authorization URL.

    The URL allows users to authenticate via Calendly and grant access to their account.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Generates and returns the Calendly OAuth authorization URL.

        Query parameters:
        - `client_id`: Calendly Client ID from settings.
        - `redirect_uri`: Redirect URI where the user is sent after authentication.

        Returns:
            Response with the Calendly authorization URL.
        """
        calendly_auth_url = "https://auth.calendly.com/oauth/authorize"
        redirect_uri = settings.CALENDLY_REDIRECT_URI
        client_id = settings.CALENDLY_CLIENT_ID
        scope = "default"
        auth_url = (
            f"{calendly_auth_url}?client_id={client_id}"
            f"&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
        )

        return Response({"auth_url": auth_url}, status=status.HTTP_200_OK)


class CalendlyCallbackView(APIView):
    """
    View to handle Calendly OAuth callback.

    Exchanges the authorization code for access and refresh tokens,
    saves the token, and fetches the user's scheduled events.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handles the Calendly OAuth callback.

        Steps:
        1. Exchanges the authorization code for access and refresh tokens.
        2. Saves the tokens to the user's profile.
        3. Fetches the mentor's scheduled events from Calendly.

        Query parameters:
        - `code`: OAuth authorization code provided by Calendly.

        Returns:
            Response with a success message or error.
        """
        code = request.query_params.get('code')
        if not code:
            return Response(
                {"error": "Authorization code missing"}, status=status.HTTP_400_BAD_REQUEST
            )

        token_url = "https://auth.calendly.com/oauth/token"
        redirect_uri = settings.CALENDLY_REDIRECT_URI
        client_id = settings.CALENDLY_CLIENT_ID
        client_secret = settings.CALENDLY_CLIENT_SECRET
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }

        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info['access_token']
            refresh_token = token_info['refresh_token']
            expires_in = token_info.get('expires_in')

            expires_at = (
                timezone.now() + timezone.timedelta(seconds=expires_in)
                if expires_in
                else None
            )

            # Save tokens to CalendlyToken model
            calendly_token, created = CalendlyToken.objects.update_or_create(
                mentor=request.user,
                defaults={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_at': expires_at
                }
            )

            # Fetch user info and scheduled events
            user_info = self.get_user_info(access_token)
            if user_info.status_code != 200:
                return Response(
                    {"error": "Failed to fetch user information"},
                    status=user_info.status_code
                )
            user_data = user_info.json()
            user_uri = user_data.get("resource", {}).get("uri")
            events_response = self.fetch_and_save_events(access_token, user_uri, request.user)
            return events_response
        else:
            return Response(response.json(), status=response.status_code)

    def get_user_info(self, access_token):
        """
        Fetches the user's information from Calendly.

        Args:
            access_token: The OAuth access token.

        Returns:
            Response object containing the user data.
        """
        user_url = "https://api.calendly.com/users/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(user_url, headers=headers)
        return response

    def fetch_and_save_events(self, access_token, user_uri, mentor):
        """
        Fetches the mentor's scheduled events from Calendly and saves them to the database.

        Args:
            access_token: The OAuth access token.
            user_uri: The URI of the Calendly user.
            mentor: The mentor object.

        Returns:
            Response with the fetched events or error message.
        """
        events_url = "https://api.calendly.com/scheduled_events"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "user": user_uri
        }
        response = requests.get(events_url, headers=headers, params=params)
        if response.status_code == 200:
            events_data = response.json()
            events = events_data.get('collection', [])
            mentor_instance = get_object_or_404(Mentor, id=mentor.id)

            # Loop through events and save them
            for event in events:
                external_id = event.get('uri')
                title = event.get('name', 'No Title')
                description = event.get('meeting_notes_plain', 'sample')
                startTime = event.get('startTime')
                endTime = event.get('endTime')
                theme = 'Meeting'
                Event.objects.update_or_create(
                    external_id=external_id,
                    defaults={
                        'mentor': mentor_instance,
                        'title': title,
                        'description': description,
                        'startTime': startTime,
                        'endTime': endTime,
                        'theme': theme
                    }
                )

            # Serialize and return the saved events
            serialized_events = EventSerializer(
                Event.objects.filter(mentor=mentor_instance),
                many=True
            ).data
            return Response({"events": serialized_events}, status=status.HTTP_200_OK)
        else:
            error_message = response.json().get('error', 'Unknown error')
            return Response({"error": error_message}, status=response.status_code)


class CalendlyEventsView(APIView):
    """
    View to fetch the mentor's scheduled events from Calendly.

    If the access token has expired, it will attempt to refresh the token.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetches the mentor's scheduled events from Calendly using the stored access token.

        Returns:
            Response with the list of events or error message.
        """
        try:
            calendly_token = request.user.calendly_token
        except CalendlyToken.DoesNotExist:
            return Response(
                {"error": "User is not authenticated or token is missing"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = calendly_token.access_token

        events_url = "https://api.calendly.com/scheduled_events"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "user": "https://api.calendly.com/users/me"
        }

        response = requests.get(events_url, headers=headers, params=params)
        if response.status_code == 200:
            events_data = response.json()
            events = events_data.get('collection', [])
            serialized_events = [
                {
                    "id": event.get('id'),
                    "title": event.get('title'),
                    "description": event.get('description'),
                    "startTime": event.get('startTime'),
                    "endTime": event.get('endTime'),
                    "theme": event.get('theme')
                }
                for event in events
            ]
            return Response({"events": serialized_events}, status=status.HTTP_200_OK)
        elif response.status_code == 401:
            return self.refresh_token_and_retry(request)
        else:
            return Response(response.json(), status=response.status_code)

    def refresh_token_and_retry(self, request):
        """
        Refreshes the expired access token and retries fetching the events.

        Returns:
            Response with the fetched events or error message.
        """
        try:
            calendly_token = request.user.calendly_token
        except CalendlyToken.DoesNotExist:
            return Response(
                {"error": "Refresh token missing"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh_token = calendly_token.refresh_token
        if not refresh_token:
            return Response(
                {"error": "Refresh token missing"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh_url = "https://auth.calendly.com/oauth/token"
        client_id = settings.CALENDLY_CLIENT_ID
        client_secret = settings.CALENDLY_CLIENT_SECRET

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }

        response = requests.post(refresh_url, data=data)
        if response.status_code == 200:
            token_info = response.json()
            calendly_token.access_token = token_info['access_token']
            calendly_token.refresh_token = token_info.get('refresh_token', refresh_token)
            calendly_token.expires_at = (
                    timezone.now() + timezone.timedelta(seconds=token_info.get('expires_in', 3600))
            )
            calendly_token.save()

            return self.get(request)
        else:
            return Response(response.json(), status=response.status_code)
