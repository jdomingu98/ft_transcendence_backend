# Generated by Django 5.0.8 on 2024-10-07 10:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_rename_total_goals_statistics_num_goals_against_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistics',
            name='time_played',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
    ]