from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.


class Statistics(models.Model):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE)

    max_streak = models.IntegerField(default=0)

    invididual_win_rate = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])

    tournament_win_rate = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])

    time_played = models.TimeField()

    punctuation = models.IntegerField(default=0)

    total_match = models.IntegerField(default=0)

    total_turney = models.IntegerField(default=0)

    total_goals = models.IntegerField(default=0)

    total_goals_against = models.IntegerField(default=0)

    total_goals_stopped = models.IntegerField(default=0)
