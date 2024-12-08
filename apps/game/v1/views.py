from rest_framework.viewsets import ModelViewSet
from ..models import LocalMatch, Tournament
from .serializers import (
    LocalMatchSerializer,
    TournamentCreateSerializer,
    TournamentStatusSerializer,
    TournamentMatchSerializer,
    ValidateMatchSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from backend.utils.tournament_utils import process_end_match


class GameViewSet(ModelViewSet):
    queryset = LocalMatch.objects.all()
    http_method_names = ['post', 'get']
    serializer_class = LocalMatchSerializer

    @action(detail=False, methods=['POST'], url_path='validate_match', url_name='validate_match', serializer_class=ValidateMatchSerializer)
    def validate_match(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TournamentViewSet(ModelViewSet):
    queryset = Tournament.objects.all()
    http_method_names = ['post', 'get']

    def get_serializer_class(self):
        if self.action == "create":
            return TournamentCreateSerializer
        elif self.action == "end_match":
            return TournamentMatchSerializer
        return TournamentStatusSerializer

    @action(detail=True, methods=['post'], url_path='end_match', url_name='end_match', serializer_class=TournamentMatchSerializer)
    def end_match(self, request, pk=None):
        tournament = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"tournament": tournament})
        serializer.is_valid(raise_exception=True)

        user_a = serializer.validated_data["user_a"]
        user_b = serializer.validated_data["user_b"]
        num_goals_scored = serializer.validated_data["num_goals_scored"]
        num_goals_against = serializer.validated_data["num_goals_against"]

        tournament = process_end_match(tournament, user_a, user_b, num_goals_scored, num_goals_against)

        return Response({
            "tournament_id": tournament.id,
            "current_round": tournament.current_round,
            "current_order_round": tournament.current_order_round,
            "total_order_round": tournament.total_order_round,
            "remaining_players": tournament.players
        }, status=status.HTTP_200_OK)
