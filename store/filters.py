import django_filters

from .models import *


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label='Search Products',
                                     lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ('name',)
