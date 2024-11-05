from rest_framework.pagination import PageNumberPagination
from apps.user.v1.serializers import LocalMatchSerializer

class UserMatchPagination(PageNumberPagination):
    page_size = 5

def paginate_matches(matches, request):
    paginator = UserMatchPagination()
    paginated_matches = paginator.paginate_queryset(matches, request)
    serializer = LocalMatchSerializer(paginated_matches, many=True)
    
    return paginator.get_paginated_response({
        'paginate': True,
        'page': paginator.page.number,
        'numItems': paginator.page_size,
        'matches': serializer.data
    })