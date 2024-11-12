from rest_framework.routers import DefaultRouter
from .views import GameViewSet, TournamentViewSet

router = DefaultRouter()

router.register(r"tournament", TournamentViewSet, basename='tournament')
router.register(r"", GameViewSet, basename='game')

urlpatterns = router.urls
