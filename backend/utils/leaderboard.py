from django.core.cache import cache
from apps.user.models import User

LEADERBOARD_CACHE_KEY = "leaderboard"
LEADERBOARD_CACHE_TIMEOUT = 60 * 15


def get_leaderboard_cached():
    user_with_ranking = cache.get(LEADERBOARD_CACHE_KEY)
    if not user_with_ranking:
        user_with_ranking = User.objects.with_ranking()[:10]
        cache.set(LEADERBOARD_CACHE_KEY, user_with_ranking, timeout=LEADERBOARD_CACHE_TIMEOUT)
    return user_with_ranking
