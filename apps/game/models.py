from django.db import models


# Create your models here.

class Statistics(models.Model):
    user_id = models.OneToOneField('user.User', on_delete=models.CASCADE)

    max_streak = models.IntegerField()

    invididual_win_rate = models.IntegerField()

    tournament_win_rate = models.IntegerField()

    time_played = models.TimeField()
    
    punctuation = models.IntegerField()

    total_match = models.IntegerField()

    total_turney = models.IntegerField()

    total_goals = models.IntegerField()

    total_goals_against = models.IntegerField()

    total_goals_stopped = models.IntegerField()

