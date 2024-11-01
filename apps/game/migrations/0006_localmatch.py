# Generated by Django 5.0.8 on 2024-10-28 12:23

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_alter_statistics_time_played'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_order', models.IntegerField(default=0)),
                ('num_round', models.IntegerField(default=0)),
                ('user_a', models.CharField()),
                ('user_b', models.CharField()),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('num_goals_scored', models.IntegerField(default=0)),
                ('num_goals_against', models.IntegerField(default=0)),
                ('num_goals_stopped_a', models.IntegerField(default=0)),
                ('num_goals_stopped_b', models.IntegerField(default=0)),
                ('time_played', models.DurationField(default=datetime.timedelta(0))),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]