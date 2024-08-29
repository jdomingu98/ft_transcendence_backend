# Generated by Django 5.0.6 on 2024-08-28 18:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0004_refreshtoken"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=255,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        code="invalid_email",
                        message="Email must be valid",
                        regex="^[\\w.-]+@([\\w-]+\\.)+[a-zA-Z]{2,3}$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                max_length=50,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        code="invalid_username",
                        message="Username must be alphanumeric or contain hyphens",
                        regex="^[a-zA-Z0-9-]*$",
                    )
                ],
            ),
        ),
    ]