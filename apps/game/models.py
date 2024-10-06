from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import datetime


class Statistics(models.Model):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE)

    max_streak = models.IntegerField(default=0)

    win_rate = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])

    time_played = models.DurationField(default=datetime.time(0,0,0))

    punctuation = models.IntegerField(default=0)

    num_matches = models.IntegerField(default=0)

    num_goals_scored = models.IntegerField(default=0)

    num_goals_against = models.IntegerField(default=0)

    num_goals_stopped = models.IntegerField(default=0)
