from rest_framework.pagination import PageNumberPagination
from apps.user.v1.serializers import LocalMatchSerializer


class PongPagination(PageNumberPagination):
    page_size = 0

    def __init__(self, page_size=5):
        self.page_size = page_size


def paginate_matches(matches, request):
    return paginate(matches, request, LocalMatchSerializer, 5)


def paginate(users, request, serializer_class, page_size):
    paginator = PongPagination(page_size=page_size)
    paginated_users = paginator.paginate_queryset(users, request)
    serializer = serializer_class(paginated_users, many=True, context={'request': request})

    return paginator.get_paginated_response({
        'paginate': True,
        'page': paginator.page.number,
        'numItems': paginator.page_size,
        'data': serializer.data
    })
