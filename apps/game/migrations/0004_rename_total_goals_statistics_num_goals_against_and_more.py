# Generated by Django 5.0.8 on 2024-09-29 10:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_rename_user_id_statistics_user_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statistics',
            old_name='total_goals',
            new_name='num_goals_against',
        ),
        migrations.RenameField(
            model_name='statistics',
            old_name='total_goals_against',
            new_name='num_goals_scored',
        ),
        migrations.RenameField(
            model_name='statistics',
            old_name='total_goals_stopped',
            new_name='num_goals_stopped',
        ),
        migrations.RenameField(
            model_name='statistics',
            old_name='total_match',
            new_name='num_matches',
        ),
        migrations.RenameField(
            model_name='statistics',
            old_name='invididual_win_rate',
            new_name='win_rate',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='total_turney',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='tournament_win_rate',
        ),
        migrations.AlterField(
            model_name='statistics',
            name='time_played',
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
    ]
