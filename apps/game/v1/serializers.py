from rest_framework import serializers
from ..models import LocalMatch, Tournament
from ..utils.update_statistics import update_statistics
from rest_framework.exceptions import ValidationError
import random
import math
from django.core.exceptions import ObjectDoesNotExist
from apps.user.models import User


class LocalMatchSerializer(serializers.ModelSerializer):
    user_a = serializers.CharField()
    user_b = serializers.CharField()
    start_date = serializers.DateTimeField()
    num_goals_scored = serializers.IntegerField()
    num_goals_against = serializers.IntegerField()
    num_goals_stopped_a = serializers.IntegerField()
    num_goals_stopped_b = serializers.IntegerField()
    time_played = serializers.DurationField()

    class Meta:
        model = LocalMatch
        fields = (
            "user_a",
            "user_b",
            "user",
            "start_date",
            "num_goals_scored",
            "num_goals_against",
            "num_goals_stopped_a",
            "num_goals_stopped_b",
            "time_played",
            "tournament",
            "num_order",
            "num_round",
        )

    def validate(self, data):
        optional_errors = {}

        if self.is_tournament(data):
            if not data.get("num_order"):
                optional_errors["num_order"] = ["ERROR.ORDER.REQUIRED"]
            if not data.get("num_round"):
                optional_errors["num_round"] = ["ERROR.ROUND.REQUIRED"]
        else:
            if not data.get("user"):
                optional_errors["user"] = ["ERROR.USER.REQUIRED"]

        if len(optional_errors) > 0:
            raise ValidationError(optional_errors)
        return data

    def create(self, validated_data):
        local_match = super().create(validated_data)
        if not self.is_tournament(validated_data):
            user = validated_data.get("user")
            update_statistics(user, local_match)
        return local_match

    def is_tournament(self, data):
        return data.get("tournament") is not None

    def is_valid(self, raise_exception=False):
        errors = {}

        try:
            super().is_valid(raise_exception=True)
        except ValidationError as e:
            errors.update(e.detail)

        try:
            self.validate(self.initial_data)
        except ValidationError as e:
            errors.update(e.detail)

        if len(errors) > 0:
            raise ValidationError(errors)

        return True

class TournamentCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    players = serializers.ListField(
        child=serializers.CharField(), required=True, min_length=2
    )
    user_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Tournament
        fields = ('name', 'players', 'user_id', 'id')

    def validate(self, data):
        players = data.get('players')
        if len(players) != len(set(players)):
            raise serializers.ValidationError({
                "players": "ERROR.TOURNAMENT.DUPLICATE_PLAYER_NAMES"
            })

        player_count = len(players)
        valid_player_counts = {2, 4, 8, 16, 32}
        if player_count not in valid_player_counts:
            raise serializers.ValidationError({
                "players": "ERROR.TOURNAMENT.INVALID_PLAYER_COUNT"
            })
        
        return data

    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)

        if user_id is not None:
            try:
                User.objects.get(id=user_id)
            except ObjectDoesNotExist:
                raise ValidationError({"user_id": "ERROR.USER.NOT_FOUND"})
        
        player_count = len(validated_data['players'])
        randomized_players = random.sample(validated_data['players'], player_count)
        total_round = int(math.log2(player_count))

        tournament = Tournament.objects.create(
            name=validated_data['name'],
            user_id=user_id,
            players=randomized_players,
            current_order_round=1,
            total_order_round=player_count // 2,
            current_round=1,
            total_round=total_round,
        )

        return tournament


class TournamentStatusSerializer(serializers.ModelSerializer):
    total_round = serializers.IntegerField(read_only=True)
    current_round = serializers.IntegerField(read_only=True)
    total_order_round = serializers.IntegerField(read_only=True)
    current_order_round = serializers.IntegerField(read_only=True)
    players = serializers.ListField(child=serializers.CharField(), read_only=True)

    class Meta:
        model = Tournament
        fields = (
            "total_round",
            "current_round",
            "total_order_round",
            "current_order_round",
            "players",
        )


class TournamentMatchSerializer(serializers.Serializer):
    user_a = serializers.CharField(required=True)
    user_b = serializers.CharField(required=True)
    num_goals_scored = serializers.IntegerField(required=True)
    num_goals_against = serializers.IntegerField(required=True)

    class Meta:
        fields = ("user_a", "user_b", "num_goals_scored", "num_goals_against")

    def validate_user_a(self, value):
        tournament = self.context["tournament"]
        if value not in tournament.players:
            raise serializers.ValidationError("ERROR.USER.NOT_IN_TOURNAMENT")
        return value
    
    def validate_user_b(self, value):
        tournament = self.context["tournament"]
        if value not in tournament.players:
            raise serializers.ValidationError("ERROR.USER.NOT_IN_TOURNAMENT")
        return value

    def validate(self, data):


        if data["num_goals_scored"] < 0 or data["num_goals_against"] < 0:
            raise serializers.ValidationError("ERROR.GOALS.INVALID")
        return data
