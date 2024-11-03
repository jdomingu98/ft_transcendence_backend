from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FriendsViewSet

router = DefaultRouter()

router.register(r"friends", FriendsViewSet, basename='friends')
router.register(r"", UserViewSet, basename='user')
urlpatterns = router.urls
