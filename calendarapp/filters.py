import django_filters
from django_filters import rest_framework as filters
from .models import Event


class EventFilters(filters.FilterSet):
    start_time = filters.DateFromToRangeFilter()
    end_time = filters.DateFromToRangeFilter()
    title = django_filters.CharFilter(field_name="title", lookup_expr='icontains')
    event_status=django_filters.ChoiceFilter(choices=[('Scheduled', 'Scheduled'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')])

    class Meta:
        model = Event
        fields = ['start_time', 'end_time', 'title', 'event_status']
