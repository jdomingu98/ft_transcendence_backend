from django.contrib.auth.models import BaseUserManager
from django.db.models import Window, F
from django.db.models.functions import RowNumber
    

class UserManager(BaseUserManager):
    def with_ranking(self):
        users_with_rank = self.annotate(
            position=Window(
                expression=RowNumber(),
                order_by=[F('statistics__punctuation').desc(), 'username']
            )
        ).order_by('position')
        return users_with_rank
