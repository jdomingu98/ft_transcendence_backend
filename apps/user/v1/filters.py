from django_filters import rest_framework as filters
from django.db.models import Q
from ..models import User


class UserFilter(filters.FilterSet):
    friends = filters.NumberFilter(method='filter_friends')

    username = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = User
        fields = ["friends", "username"]

    def filter_friends(self, queryset, name, value):
        return queryset.filter(
            Q(friendships_requested__friend=value, friendships_requested__accepted=True) | # noqa
            Q(friendships_received__user=value, friendships_received__accepted=True)
        ) if value else queryset
