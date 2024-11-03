from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from apps.user.v1.serializers import LocalMatchSerializer
from apps.user.models import User
from apps.game.models import LocalMatch

class UserMatchPagination(PageNumberPagination):
    page_size = 5

def fetch_user_matches(user_id):
    user = get_object_or_404(User, pk=user_id)
    return LocalMatch.objects.filter(Q(user_a=user) | Q(user_b=user))

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

def get_user_matches(user_id, request):
    matches = fetch_user_matches(user_id)
    return paginate_matches(matches, request)