# Generated by Django 5.0.8 on 2024-11-18 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_statistics_num_matches_defeat_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statistics',
            name='num_matches_defeat',
        ),
        migrations.AddField(
            model_name='statistics',
            name='current_streak',
            field=models.IntegerField(default=0),
        ),
    ]
