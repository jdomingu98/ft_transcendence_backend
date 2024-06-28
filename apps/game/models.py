from django.db import models


# Create your models here.

class Statistics(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE)

    max_streak = models.IntegerField(default=0)

    invididual_win_rate = models.IntegerField(default=0)

    tournament_win_rate = models.IntegerField(default=0)

    time_played = models.TimeField(default=None)
    
    punctuation = models.IntegerField(default=0)

    total_match = models.IntegerField(default=0)

    total_turney = models.IntegerField(default=0)

    total_goals = models.IntegerField(default=0)

    total_goals_against = models.IntegerField(default=0)

    total_goals_stopped = models.IntegerField(default=0)