from rest_framework import serializers
from .models import LocalMatch
from .utils.update_statistics import update_statistics
from rest_framework.exceptions import ValidationError

class LocalMatchSerializer(serializers.ModelSerializer):
    user_a = serializers.CharField()
    user_b = serializers.CharField()
    start_date = serializers.DateTimeField()
    num_goals_scored = serializers.IntegerField()
    num_goals_against = serializers.IntegerField()
    num_goals_stopped_a = serializers.IntegerField()
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

        if self.is_tourney(data):
            if not data.get("num_order"):
                optional_errors["num_order"] = ["This field is required."]
            if not data.get("num_round"):
                optional_errors["num_round"] = ["This field is required."]
        else:
            if not data.get("user"):
                optional_errors["user"] = ["This field is required."]

        if len(optional_errors) > 0:
            raise ValidationError(optional_errors)
        return data

    def create(self, validated_data):
        local_match = super().create(validated_data)
        if not self.is_tourney(validated_data):
            user = validated_data.get("user")
            update_statistics(user, local_match)
        return local_match

    def is_tourney(self, data):
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