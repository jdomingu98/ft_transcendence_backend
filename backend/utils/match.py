from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from apps.user.v1.serializers import LocalMatchSerializer
from apps.user.models import User, LocalMatch

class UserMatchPagination(PageNumberPagination):
    page_size = 5

def fetch_user_matches(user_id):
    user = get_object_or_404(User, pk=user_id)
    return LocalMatch.objects.filter(Q(user_a=user) | Q(user_b=user))

def calculate_match_results(matches):
    for match in matches:
        if match.num_goals_scored > match.num_goals_against:
            match.result = 'victory'
            match.earned = 10
        elif match.num_goals_scored < match.num_goals_against:
            match.result = 'defeat'
            match.earned = -5
        else:
            match.result = 'draw'
            match.earned = 0

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
    calculate_match_results(matches)
    return paginate_matches(matches, request)
