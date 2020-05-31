import django_filters

from .models import *


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ('name',)
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
