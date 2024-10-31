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
        errors = self.errors
        if self.is_tourney(data):
            print("ES UN TORNEO")
            if not data.get("num_order"):
                errors["num_order"] = ["REQUIRED"]
            if not data.get("num_round"):
                errors["num_round"] = ["REQUIRED"]
        else:
            print("NO ES UN TORNETO")
            if not data.get("user"):
                print("NO AHI USUARIO")
                errors["user"] = ["REQUIRED"]

        if len(errors) > 0:
            raise ValidationError(errors)

    def create(self, validated_data):
        local_match = super().create(validated_data)
        if not self.is_tourney(validated_data):
            user = validated_data.get("user")
            update_statistics(user, local_match)
            return local_match
        else:
            pass

    def is_tourney(self, data):
        print("TIPO:", data.get("tournament"))
        return data.get("tournament") is not None

    
    def is_valid(self, raise_exception=False):
        try:
            super().is_valid(raise_exception=True)
        except:
            print("INITAL DATA:", self.initial_data)
            self.validate(self.initial_data)
        return True
        