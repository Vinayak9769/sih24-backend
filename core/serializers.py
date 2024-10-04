from rest_framework import serializers
from .models import Mentor, Category
from .models import MentorAvailability
from calendarapp.models import Event
from datetime import datetime, timedelta, date


class MentorSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
        allow_null=True,
        help_text="List of category IDs the mentor specializes in."
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Password for the mentor account.",
        style={'input_type': 'password'}
    )

    class Meta:
        model = Mentor
        fields = [
            'id', 'username', 'password', 'email', 'name', 'bio',
            'profile_picture', 'phone_number', 'description',
            'expertise', 'linkedin_profile', 'categories',
            'price', 'experience', 'company'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        password = validated_data.pop('password', None)
        user = Mentor(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        user.categories.set(categories)
        return user


class MentorAvailabilitySerializer(serializers.ModelSerializer):
    day = serializers.CharField(source='day_of_week')
    startTime = serializers.TimeField(source='start_time')
    endTime = serializers.TimeField(source='end_time')

    class Meta:
        model = MentorAvailability
        fields = ['day', 'startTime', 'endTime']
        extra_kwargs = {
            'start_time': {'source': 'startTime'},
            'end_time': {'source': 'endTime'},
            'day_of_week': {'source': 'day'}
        }

    def get_available_slots(self, date, mentor, start_time, end_time):
        one_hour = timedelta(hours=1)
        slots = []

        while start_time + one_hour <= end_time:
            slot_start = start_time
            slot_end = start_time + one_hour

            events = Event.objects.filter(
                mentor=mentor,
                start_time__lt=slot_end,
                end_time__gt=slot_start,
                start_time__date=date
            )

            if not events.exists():
                slots.append({
                    "start": slot_start.strftime('%Y-%m-%d %H:%M'),
                    "end": slot_end.strftime('%Y-%m-%d %H:%M')
                })

            start_time += one_hour

        return slots

    def to_representation(self, instance):
        data = super().to_representation(instance)
        mentor = self.context['mentor']
        date_str = self.context.get('date')
        data['startTime'] = data.pop('startTime')
        data['endTime'] = data.pop('endTime')
        data['day'] = data.pop('day')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                start_time = datetime.combine(date, instance.start_time)
                end_time = datetime.combine(date, instance.end_time)
                slots = self.get_available_slots(date, mentor, start_time, end_time)
                data['slots'] = slots
                data['date'] = date_str
            except ValueError:
                data['slots'] = []
        else:
            data['slots'] = []



        return data

    def validate(self, data):
        return data


