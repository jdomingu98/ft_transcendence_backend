from enum import Enum
from django.db import models


class Visibility(Enum):
    PUBLIC = 1
    PRIVATE = 2
    ANONYMOUS = 3


class Language(models.TextChoices):
    SPANISH = 'es', 'Spanish'
    ENGLISH = 'en', 'English'
    FRENCH = 'fr', 'French'
