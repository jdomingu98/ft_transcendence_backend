from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from .enums import Language, Visibility


class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)

    email = models.EmailField(max_length=255, unique=True)

    profile_img = models.FileField(max_length=200, null=True)

    banner = models.FileField(max_length=200, null=True)

    visibility = models.IntegerField(
        choices=[(tag.value, tag.name) for tag in Visibility],
        default=Visibility.PUBLIC.value,
    )

    is_connected = models.BooleanField(default=True)

    language = models.CharField(choices=Language.choices, default=Language.SPANISH.value, max_length=2)

    USERNAME_FIELD = "username"
    objects = BaseUserManager()


class RefreshToken(models.Model):
    token = models.CharField(max_length=1024, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
