from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FriendsViewSet

router = DefaultRouter()

router.register(r"", UserViewSet, basename='user')
router.register(r"(?P<user_pk>[^/.]+)/friends", FriendsViewSet, basename='friends')
urlpatterns = router.urls
