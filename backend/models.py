from django.db import models
from enums import Visibility, Lenguage

class User(models.Model):
    ID_User = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    profile_img = models.CharField(max_length=200, unique=True, null=True)
    banner = models.CharField(max_length=200, unique=True, null=True)
    visibility = models.IntegerField(choices=[(tag.value, tag.name) for tag in Visibility],
                                     default=Visibility.PUBLIC.value)
    status = models.BooleanField(default=True)
    id_42 = models.CharField(unique=True)
    lenguage = models.IntegerField(choices=[(tag.value, tag.name) for tag in Lenguage],
                                    default=Lenguage.SPANISH.value)