# Generated by Django 5.0.6 on 2024-08-05 16:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_alter_statistics_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statistics',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='statistics',
            name='invididual_win_rate',
            field=models.IntegerField(default=100, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='max_streak',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='punctuation',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='total_goals',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='total_goals_against',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='total_goals_stopped',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='total_match',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='total_turney',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='tournament_win_rate',
            field=models.IntegerField(default=100, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
