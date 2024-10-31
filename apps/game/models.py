from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import datetime


class Statistics(models.Model):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE)

    max_streak = models.IntegerField(default=0)

    win_rate = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])

    time_played = models.DurationField(default=datetime.timedelta(0))

    punctuation = models.IntegerField(default=0)

    num_matches = models.IntegerField(default=0)

    num_matches_won = models.IntegerField(default=0)

    num_goals_scored = models.IntegerField(default=0)

    num_goals_against = models.IntegerField(default=0)

    num_goals_stopped = models.IntegerField(default=0)


class LocalMatch(models.Model):
    num_order = models.IntegerField(default=0)

    num_round = models.IntegerField(default=0)

    user_a = models.CharField(null=True)

    user_b = models.CharField(null=True)

    user = models.ForeignKey("user.User", on_delete=models.CASCADE, null=True)

    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE, null=True)

    start_date = models.DateTimeField(auto_now_add=True)

    num_goals_scored = models.IntegerField(default=0)

    num_goals_against = models.IntegerField(default=0)

    num_goals_stopped_a = models.IntegerField(default=0)

    num_goals_stopped_b = models.IntegerField(default=0)

    time_played = models.DurationField(default=datetime.timedelta(0))


class Tournament(models.Model):
    name = models.CharField(max_length=50)

    user = models.ForeignKey("user.User", on_delete=models.CASCADE, null=True)
   
    players = models.CharField(max_length=500)

    current_order_round = models.IntegerField(default=0)

    total_order_round = models.IntegerField(default=0)

    current_round = models.IntegerField(default=0)

    total_round = models.IntegerField(default=0)
