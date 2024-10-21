from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.core.validators import RegexValidator

from .enums import Language, Visibility
from apps.game.models import Statistics
from .manager import UserManager


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9-]*$",
                message="Username must be alphanumeric or contain hyphens",
                code="invalid_username",
            ),
        ],
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
    )

    friends = models.ManyToManyField("user.User",through="user.FriendShip")

    profile_img = models.FileField(max_length=200, null=True)

    banner = models.FileField(max_length=200, null=True)

    visibility = models.IntegerField(
        choices=[(tag.value, tag.name) for tag in Visibility],
        default=Visibility.PUBLIC.value,
    )

    is_connected = models.BooleanField(default=True)

    is_verified = models.BooleanField(default=False)

    language = models.CharField(choices=Language.choices, default=Language.SPANISH.value, max_length=2)

    id42 = models.TextField(null=True)

    two_factor_enabled = models.BooleanField(default=False, blank=True)

    USERNAME_FIELD = "username"
    objects = UserManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not hasattr(self, 'statistics'):
            Statistics.objects.create(user=self)


class OTPCode(models.Model):
    code = models.CharField(max_length=6, unique=True)
    expiration_time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class RefreshToken(models.Model):
    token = models.CharField(max_length=1024, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class FriendShip(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='friendships_requested')
    friend = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='friendships_received')
    accepted = models.BooleanField(default=False)