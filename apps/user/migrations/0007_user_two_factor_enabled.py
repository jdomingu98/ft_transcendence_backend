# Generated by Django 5.0.8 on 2024-09-25 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_user_id42'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='two_factor_enabled',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
