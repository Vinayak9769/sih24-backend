import django_filters
from .models import Mentor
from .models import Category


class MentorFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    categories = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        field_name='categories',
    )
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    order_by = django_filters.OrderingFilter(
        fields=(
            ('price', 'price'),
            ('name', 'name'),
        ),
        field_labels={
            'price': 'Price',
            'name': 'Name',
        }
    )

    class Meta:
        model = Mentor
        fields = ['categories', 'min_price', 'max_price', 'name', 'order_by']
