from django_filters import rest_framework as filters
from ..models import User


class UserFilter(filters.FilterSet):
    friends = filters.NumberFilter(method='filter_friends')

    username = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = User
        fields = ["friends", "username"]

    def filter_friends(self, queryset, name, value):
        return queryset.filter(friends__id=value) if value else queryset
