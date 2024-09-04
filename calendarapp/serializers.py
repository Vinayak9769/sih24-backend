from rest_framework import serializers
from .models import Event
from datetime import datetime
from .helper import make_naive


class EventSerializer(serializers.ModelSerializer):
    startDateTime = serializers.DateTimeField(source='start_time')
    endDateTime = serializers.DateTimeField(source='end_time')
    name = serializers.CharField(source='title')
    status = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'startDateTime', 'endDateTime', 'status', 'theme', 'mentee']
        extra_kwargs = {
            'mentee': {'required': False, 'write_only': True}
        }

    def get_status(self, obj):
        now = make_naive(datetime.now())
        start_time = make_naive(obj.start_time)
        end_time = make_naive(obj.end_time)

        if end_time < now:
            return 'Completed'
        elif start_time <= now <= end_time:
            return 'Ongoing'
        else:
            return 'Scheduled'


class ScheduleMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['mentor', 'title', 'description', 'start_time', 'end_time']

    def validate(self, data):
        mentor = data.get('mentor')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        if start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")
        overlapping_events = Event.objects.filter(
            mentor=mentor,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if overlapping_events.exists():
            raise serializers.ValidationError("This time slot is already booked for the mentor.")

        return data

