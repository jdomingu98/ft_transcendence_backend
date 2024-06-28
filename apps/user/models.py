from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from .enums import Visibility, Language


class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)

    email = models.EmailField(max_length=255, unique=True)

    profile_img = models.FileField(max_length=200, null=True)

    banner = models.FileField(max_length=200, null=True)

    visibility = models.IntegerField(
        choices=[(tag.value, tag.name) for tag in Visibility],
        default=Visibility.PUBLIC.value
    )

    is_connected = models.BooleanField(default=True)

    language = models.CharField(
        choices=Language.choices,
        default=Language.SPANISH.value,
        max_length=2
    )

    USERNAME_FIELD = 'username'
    objects = BaseUserManager()