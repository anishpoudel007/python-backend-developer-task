# products/filters.py
import django_filters
from django.db.models import Q
from .models import Product


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_search")
    min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="lte")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    category_id = django_filters.UUIDFilter(field_name="category_id")
    active = django_filters.NumberFilter(field_name="active")  # <-- use NumberFilter

    class Meta:
        model = Product
        fields = ["q", "category_id", "active", "in_stock", "min_price", "max_price"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(code__icontains=value) | Q(description__icontains=value)
        )

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity__lte=0)
