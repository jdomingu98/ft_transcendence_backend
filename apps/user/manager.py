from django.contrib.auth.models import BaseUserManager
from django.db.models import Q, Count, OuterRef, Subquery
from apps.game.models import Statistics

class UserManager(BaseUserManager):
    def with_ranking(self):
        rank_subquery = (
            Statistics.objects.filter(
                Q(punctuation__gte=OuterRef('statistics__punctuation'))
                |  Q(punctuation=OuterRef('statistics__punctuation'), user__username__lt=OuterRef('username'))
            )
            .values('punctuation')
            .annotate(rank=Count('punctuation'))
        )
        
        return self.get_queryset().annotate(
            position=Subquery(rank_subquery.values('rank')[:1])
        ).order_by('position', 'username')