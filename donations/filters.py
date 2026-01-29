# from rest_framework import
from django_filters import FilterSet, NumberFilter
from donations.models import Donations

class DonationFilterSet(FilterSet):
    avg_rating__gte = NumberFilter(field_name='avg_rating', lookup_expr='gte')

    class Meta:
        model = Donations
        fields = {
            'target_amount': ['exact', 'gte', 'lte'],
            'start_date': ['exact', 'year__gt', 'year__lt'],
            'end_date': ['exact', 'year__gt', 'year__lt'],
            'status': ['icontains'],
            'category': ['exact'],
            'category__category_name': ['icontains', 'exact'],
        }